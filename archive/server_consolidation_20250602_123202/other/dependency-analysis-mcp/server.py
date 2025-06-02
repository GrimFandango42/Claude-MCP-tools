#!/usr/bin/env python3
"""
Dependency Analysis MCP Server

Provides comprehensive dependency analysis capabilities including:
- Security vulnerability scanning
- License compliance checking
- Version compatibility analysis
- Unused dependency detection
- Update recommendations with risk assessment
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import re

from fastmcp import FastMCP
from pythonjsonlogger import jsonlogger
import aiofiles
import aiohttp
import requests
from packaging import version
from pydantic import BaseModel


# Initialize FastMCP server
mcp = FastMCP("dependency-analysis-mcp")


def setup_logging():
    """Setup structured logging for MCP server"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add stderr handler with JSON formatting
    handler = logging.StreamHandler(sys.stderr)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@dataclass
class Vulnerability:
    """Represents a security vulnerability"""
    id: str
    package: str
    installed_version: str
    vulnerable_spec: str
    fixed_version: Optional[str]
    severity: str
    description: str
    cve_id: Optional[str] = None
    advisory_url: Optional[str] = None


@dataclass
class LicenseInfo:
    """Represents license information for a package"""
    package: str
    version: str
    license: str
    license_type: str  # "permissive", "copyleft", "proprietary", "unknown"
    compatibility_score: float  # 0-100, higher is better
    restrictions: List[str]


@dataclass
class DependencyUpdate:
    """Represents a potential dependency update"""
    package: str
    current_version: str
    latest_version: str
    update_type: str  # "major", "minor", "patch"
    risk_level: str  # "low", "medium", "high"
    breaking_changes: bool
    security_fixes: bool
    changelog_url: Optional[str] = None


class SecurityScanner:
    """Security vulnerability scanner"""
    
    async def run_command(self, command: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """Run a shell command and return structured result"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "command": ' '.join(command)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": ' '.join(command)
            }
    
    async def scan_python_vulnerabilities(self, project_path: str) -> List[Vulnerability]:
        """Scan Python dependencies for vulnerabilities using pip-audit"""
        vulnerabilities = []
        
        try:
            # Run pip-audit
            result = await self.run_command([
                "pip-audit", "--format=json", "--requirement", "requirements.txt"
            ], cwd=project_path)
            
            if result["success"] and result["stdout"]:
                try:
                    audit_data = json.loads(result["stdout"])
                    
                    for vuln in audit_data.get("vulnerabilities", []):
                        vulnerability = Vulnerability(
                            id=vuln.get("id", ""),
                            package=vuln.get("package", ""),
                            installed_version=vuln.get("installed_version", ""),
                            vulnerable_spec=vuln.get("vulnerable_spec", ""),
                            fixed_version=vuln.get("fixed_version"),
                            severity=vuln.get("severity", "unknown"),
                            description=vuln.get("description", ""),
                            cve_id=vuln.get("cve_id"),
                            advisory_url=vuln.get("advisory_url")
                        )
                        vulnerabilities.append(vulnerability)
                        
                except json.JSONDecodeError:
                    logging.error("Failed to parse pip-audit output")
            
            # Also try safety scanner as backup
            safety_result = await self.run_command([
                "safety", "check", "--json"
            ], cwd=project_path)
            
            if safety_result["success"] and safety_result["stdout"]:
                try:
                    safety_data = json.loads(safety_result["stdout"])
                    
                    for vuln in safety_data:
                        vulnerability = Vulnerability(
                            id=vuln.get("id", ""),
                            package=vuln.get("package", ""),
                            installed_version=vuln.get("installed_version", ""),
                            vulnerable_spec=vuln.get("vulnerable_spec", ""),
                            fixed_version=None,
                            severity=vuln.get("severity", "medium"),
                            description=vuln.get("vulnerability", ""),
                            cve_id=vuln.get("cve")
                        )
                        
                        # Avoid duplicates
                        if not any(v.id == vulnerability.id and v.package == vulnerability.package 
                                 for v in vulnerabilities):
                            vulnerabilities.append(vulnerability)
                            
                except json.JSONDecodeError:
                    logging.error("Failed to parse safety output")
            
        except Exception as e:
            logging.error(f"Vulnerability scanning failed: {e}")
        
        return vulnerabilities
    
    async def scan_javascript_vulnerabilities(self, project_path: str) -> List[Vulnerability]:
        """Scan JavaScript dependencies for vulnerabilities using npm audit"""
        vulnerabilities = []
        
        try:
            result = await self.run_command([
                "npm", "audit", "--json"
            ], cwd=project_path)
            
            if result["stdout"]:
                try:
                    audit_data = json.loads(result["stdout"])
                    
                    for vuln_id, vuln_data in audit_data.get("vulnerabilities", {}).items():
                        vulnerability = Vulnerability(
                            id=vuln_id,
                            package=vuln_data.get("name", ""),
                            installed_version=vuln_data.get("version", ""),
                            vulnerable_spec=vuln_data.get("range", ""),
                            fixed_version=vuln_data.get("fixAvailable", {}).get("version"),
                            severity=vuln_data.get("severity", "unknown"),
                            description=vuln_data.get("title", ""),
                            cve_id=vuln_data.get("cve", [None])[0] if vuln_data.get("cve") else None,
                            advisory_url=vuln_data.get("url")
                        )
                        vulnerabilities.append(vulnerability)
                        
                except json.JSONDecodeError:
                    logging.error("Failed to parse npm audit output")
            
        except Exception as e:
            logging.error(f"JavaScript vulnerability scanning failed: {e}")
        
        return vulnerabilities


class LicenseAnalyzer:
    """License compliance analyzer"""
    
    def __init__(self):
        self.license_compatibility = {
            "MIT": {"type": "permissive", "score": 100, "restrictions": []},
            "Apache-2.0": {"type": "permissive", "score": 95, "restrictions": ["patent_notice"]},
            "BSD-3-Clause": {"type": "permissive", "score": 100, "restrictions": []},
            "GPL-3.0": {"type": "copyleft", "score": 60, "restrictions": ["source_disclosure", "copyleft"]},
            "LGPL-3.0": {"type": "copyleft", "score": 75, "restrictions": ["limited_copyleft"]},
            "ISC": {"type": "permissive", "score": 100, "restrictions": []},
            "MPL-2.0": {"type": "copyleft", "score": 80, "restrictions": ["file_copyleft"]},
            "Proprietary": {"type": "proprietary", "score": 30, "restrictions": ["usage_restrictions", "redistribution_forbidden"]},
            "Unknown": {"type": "unknown", "score": 0, "restrictions": ["unknown_terms"]}
        }
    
    async def analyze_python_licenses(self, project_path: str) -> List[LicenseInfo]:
        """Analyze licenses of Python dependencies"""
        licenses = []
        
        try:
            # Get installed packages with pip show
            result = await self._run_pip_show(project_path)
            
            for package_info in result:
                license_name = package_info.get("License", "Unknown")
                license_data = self.license_compatibility.get(license_name, 
                                                            self.license_compatibility["Unknown"])
                
                license_info = LicenseInfo(
                    package=package_info.get("Name", ""),
                    version=package_info.get("Version", ""),
                    license=license_name,
                    license_type=license_data["type"],
                    compatibility_score=license_data["score"],
                    restrictions=license_data["restrictions"]
                )
                licenses.append(license_info)
        
        except Exception as e:
            logging.error(f"License analysis failed: {e}")
        
        return licenses
    
    async def _run_pip_show(self, project_path: str) -> List[Dict[str, str]]:
        """Get package information using pip show"""
        packages = []
        
        # First, get list of installed packages
        result = await self._run_command(["pip", "list", "--format=json"], project_path)
        
        if result["success"] and result["stdout"]:
            try:
                package_list = json.loads(result["stdout"])
                
                for package in package_list:
                    # Get detailed info for each package
                    show_result = await self._run_command([
                        "pip", "show", package["name"]
                    ], project_path)
                    
                    if show_result["success"]:
                        package_info = self._parse_pip_show_output(show_result["stdout"])
                        packages.append(package_info)
                        
            except json.JSONDecodeError:
                logging.error("Failed to parse pip list output")
        
        return packages
    
    def _parse_pip_show_output(self, output: str) -> Dict[str, str]:
        """Parse pip show output into dictionary"""
        info = {}
        for line in output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()
        return info
    
    async def _run_command(self, command: List[str], cwd: str) -> Dict[str, Any]:
        """Helper to run commands"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_license_compatibility(self, licenses: List[LicenseInfo], 
                                  allowed_licenses: List[str]) -> Dict[str, Any]:
        """Check license compatibility against allowed list"""
        compatible = []
        incompatible = []
        unknown = []
        
        for license_info in licenses:
            if license_info.license in allowed_licenses:
                compatible.append(license_info)
            elif license_info.license == "Unknown":
                unknown.append(license_info)
            else:
                incompatible.append(license_info)
        
        return {
            "compatible": [
                {
                    "package": lic.package,
                    "license": lic.license,
                    "compatibility_score": lic.compatibility_score
                }
                for lic in compatible
            ],
            "incompatible": [
                {
                    "package": lic.package,
                    "license": lic.license,
                    "restrictions": lic.restrictions
                }
                for lic in incompatible
            ],
            "unknown": [
                {
                    "package": lic.package,
                    "version": lic.version
                }
                for lic in unknown
            ],
            "summary": {
                "total_packages": len(licenses),
                "compatible_count": len(compatible),
                "incompatible_count": len(incompatible),
                "unknown_count": len(unknown),
                "compliance_score": len(compatible) / len(licenses) * 100 if licenses else 100
            }
        }


class DependencyAnalyzer:
    """Comprehensive dependency analysis"""
    
    def __init__(self):
        self.security_scanner = SecurityScanner()
        self.license_analyzer = LicenseAnalyzer()
    
    async def analyze_project_dependencies(self, project_path: str, 
                                         language: str = "auto") -> Dict[str, Any]:
        """Perform comprehensive dependency analysis"""
        analysis = {
            "project_path": project_path,
            "language": language,
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "licenses": [],
            "updates": [],
            "unused_dependencies": [],
            "dependency_tree": {},
            "summary": {}
        }
        
        # Detect language if auto
        if language == "auto":
            language = self._detect_project_language(project_path)
        
        analysis["language"] = language
        
        try:
            # Security vulnerability analysis
            if language == "python":
                analysis["vulnerabilities"] = await self.security_scanner.scan_python_vulnerabilities(project_path)
                analysis["licenses"] = await self.license_analyzer.analyze_python_licenses(project_path)
            elif language == "javascript":
                analysis["vulnerabilities"] = await self.security_scanner.scan_javascript_vulnerabilities(project_path)
            
            # Analyze dependency updates
            analysis["updates"] = await self._analyze_available_updates(project_path, language)
            
            # Find unused dependencies
            analysis["unused_dependencies"] = await self._find_unused_dependencies(project_path, language)
            
            # Generate summary
            analysis["summary"] = self._generate_analysis_summary(analysis)
            
        except Exception as e:
            logging.error(f"Dependency analysis failed: {e}")
            analysis["error"] = str(e)
        
        return analysis
    
    def _detect_project_language(self, project_path: str) -> str:
        """Detect the primary language of the project"""
        files = os.listdir(project_path)
        
        if "requirements.txt" in files or "pyproject.toml" in files or "setup.py" in files:
            return "python"
        elif "package.json" in files:
            return "javascript"
        elif "Gemfile" in files:
            return "ruby"
        elif "pom.xml" in files or "build.gradle" in files:
            return "java"
        else:
            return "unknown"
    
    async def _analyze_available_updates(self, project_path: str, language: str) -> List[DependencyUpdate]:
        """Analyze available dependency updates"""
        updates = []
        
        try:
            if language == "python":
                updates = await self._analyze_python_updates(project_path)
            elif language == "javascript":
                updates = await self._analyze_javascript_updates(project_path)
        
        except Exception as e:
            logging.error(f"Update analysis failed: {e}")
        
        return updates
    
    async def _analyze_python_updates(self, project_path: str) -> List[DependencyUpdate]:
        """Analyze Python dependency updates"""
        updates = []
        
        try:
            # Use pip list --outdated
            result = await self.security_scanner.run_command([
                "pip", "list", "--outdated", "--format=json"
            ], cwd=project_path)
            
            if result["success"] and result["stdout"]:
                outdated_packages = json.loads(result["stdout"])
                
                for package in outdated_packages:
                    current = package.get("version", "")
                    latest = package.get("latest_version", "")
                    
                    if current and latest:
                        update_type = self._determine_update_type(current, latest)
                        risk_level = self._assess_update_risk(update_type, package.get("name", ""))
                        
                        update = DependencyUpdate(
                            package=package.get("name", ""),
                            current_version=current,
                            latest_version=latest,
                            update_type=update_type,
                            risk_level=risk_level,
                            breaking_changes=update_type == "major",
                            security_fixes=False  # Would need additional API calls to determine
                        )
                        updates.append(update)
        
        except Exception as e:
            logging.error(f"Python update analysis failed: {e}")
        
        return updates
    
    async def _analyze_javascript_updates(self, project_path: str) -> List[DependencyUpdate]:
        """Analyze JavaScript dependency updates"""
        updates = []
        
        try:
            # Use npm outdated
            result = await self.security_scanner.run_command([
                "npm", "outdated", "--json"
            ], cwd=project_path)
            
            if result["stdout"]:
                try:
                    outdated_data = json.loads(result["stdout"])
                    
                    for package_name, package_info in outdated_data.items():
                        current = package_info.get("current", "")
                        latest = package_info.get("latest", "")
                        
                        if current and latest:
                            update_type = self._determine_update_type(current, latest)
                            risk_level = self._assess_update_risk(update_type, package_name)
                            
                            update = DependencyUpdate(
                                package=package_name,
                                current_version=current,
                                latest_version=latest,
                                update_type=update_type,
                                risk_level=risk_level,
                                breaking_changes=update_type == "major",
                                security_fixes=False
                            )
                            updates.append(update)
                            
                except json.JSONDecodeError:
                    pass  # npm outdated returns non-JSON when no updates
        
        except Exception as e:
            logging.error(f"JavaScript update analysis failed: {e}")
        
        return updates
    
    def _determine_update_type(self, current: str, latest: str) -> str:
        """Determine if update is major, minor, or patch"""
        try:
            current_ver = version.parse(current)
            latest_ver = version.parse(latest)
            
            if latest_ver.major > current_ver.major:
                return "major"
            elif latest_ver.minor > current_ver.minor:
                return "minor"
            else:
                return "patch"
        except:
            return "unknown"
    
    def _assess_update_risk(self, update_type: str, package_name: str) -> str:
        """Assess the risk level of an update"""
        if update_type == "major":
            return "high"
        elif update_type == "minor":
            return "medium"
        else:
            return "low"
    
    async def _find_unused_dependencies(self, project_path: str, language: str) -> List[str]:
        """Find dependencies that appear to be unused"""
        unused = []
        
        try:
            if language == "python":
                unused = await self._find_unused_python_dependencies(project_path)
            elif language == "javascript":
                unused = await self._find_unused_javascript_dependencies(project_path)
        
        except Exception as e:
            logging.error(f"Unused dependency analysis failed: {e}")
        
        return unused
    
    async def _find_unused_python_dependencies(self, project_path: str) -> List[str]:
        """Find unused Python dependencies"""
        unused = []
        
        try:
            # This is a simplified implementation
            # In practice, would use tools like unimport or analyze import statements
            
            # Read requirements.txt
            requirements_file = os.path.join(project_path, "requirements.txt")
            if os.path.exists(requirements_file):
                async with aiofiles.open(requirements_file, 'r') as f:
                    requirements = await f.read()
                
                # Extract package names
                required_packages = []
                for line in requirements.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        package = re.split(r'[>=<!=]', line)[0].strip()
                        required_packages.append(package)
                
                # Check if packages are imported (simplified)
                imported_packages = await self._find_imported_packages(project_path)
                
                for package in required_packages:
                    if package.lower() not in [imp.lower() for imp in imported_packages]:
                        unused.append(package)
        
        except Exception as e:
            logging.error(f"Python unused dependency analysis failed: {e}")
        
        return unused
    
    async def _find_imported_packages(self, project_path: str) -> Set[str]:
        """Find all imported packages in Python code"""
        imported = set()
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                            content = await f.read()
                        
                        # Simple regex to find imports
                        import_matches = re.findall(r'^\s*(?:import|from)\s+(\w+)', content, re.MULTILINE)
                        imported.update(import_matches)
                        
                    except:
                        continue
        
        return imported
    
    async def _find_unused_javascript_dependencies(self, project_path: str) -> List[str]:
        """Find unused JavaScript dependencies"""
        # This would use tools like depcheck
        return []  # Simplified for now
    
    def _generate_analysis_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of dependency analysis"""
        vulnerabilities = analysis.get("vulnerabilities", [])
        updates = analysis.get("updates", [])
        unused = analysis.get("unused_dependencies", [])
        
        severity_counts = {}
        for vuln in vulnerabilities:
            severity = vuln.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        update_counts = {}
        for update in updates:
            risk = update.risk_level
            update_counts[risk] = update_counts.get(risk, 0) + 1
        
        return {
            "total_vulnerabilities": len(vulnerabilities),
            "vulnerability_severity": severity_counts,
            "critical_vulnerabilities": severity_counts.get("critical", 0),
            "high_vulnerabilities": severity_counts.get("high", 0),
            "total_updates_available": len(updates),
            "update_risk_distribution": update_counts,
            "high_risk_updates": update_counts.get("high", 0),
            "unused_dependencies_count": len(unused),
            "security_score": self._calculate_security_score(vulnerabilities),
            "maintenance_score": self._calculate_maintenance_score(updates, unused)
        }
    
    def _calculate_security_score(self, vulnerabilities: List[Vulnerability]) -> float:
        """Calculate security score (0-100, higher is better)"""
        if not vulnerabilities:
            return 100.0
        
        # Weight by severity
        severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}
        total_weight = sum(severity_weights.get(vuln.severity, 1) for vuln in vulnerabilities)
        
        # Score decreases with more/severe vulnerabilities
        return max(0, 100 - (total_weight * 5))
    
    def _calculate_maintenance_score(self, updates: List[DependencyUpdate], 
                                   unused: List[str]) -> float:
        """Calculate maintenance score (0-100, higher is better)"""
        score = 100.0
        
        # Deduct for outdated packages
        score -= len(updates) * 2
        
        # Deduct more for high-risk updates
        high_risk_updates = sum(1 for update in updates if update.risk_level == "high")
        score -= high_risk_updates * 5
        
        # Deduct for unused dependencies
        score -= len(unused) * 3
        
        return max(0, score)


# Initialize analyzer
dependency_analyzer = DependencyAnalyzer()


@mcp.tool()
async def scan_vulnerabilities(project_path: str, language: str = "auto") -> Dict[str, Any]:
    """
    Scan project dependencies for security vulnerabilities.
    
    Args:
        project_path: Root path of the project to scan
        language: Programming language ("python", "javascript", "auto")
    
    Returns:
        Dictionary containing vulnerability scan results
    """
    try:
        logging.info(f"Scanning vulnerabilities in: {project_path}")
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"Project path not found: {project_path}"
            }
        
        # Detect language if auto
        if language == "auto":
            language = dependency_analyzer._detect_project_language(project_path)
        
        vulnerabilities = []
        
        if language == "python":
            vulnerabilities = await dependency_analyzer.security_scanner.scan_python_vulnerabilities(project_path)
        elif language == "javascript":
            vulnerabilities = await dependency_analyzer.security_scanner.scan_javascript_vulnerabilities(project_path)
        else:
            return {
                "success": False,
                "error": f"Language '{language}' not supported for vulnerability scanning"
            }
        
        # Organize by severity
        by_severity = {}
        for vuln in vulnerabilities:
            severity = vuln.severity
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append({
                "id": vuln.id,
                "package": vuln.package,
                "installed_version": vuln.installed_version,
                "fixed_version": vuln.fixed_version,
                "description": vuln.description,
                "cve_id": vuln.cve_id,
                "advisory_url": vuln.advisory_url
            })
        
        return {
            "success": True,
            "project_path": project_path,
            "language": language,
            "total_vulnerabilities": len(vulnerabilities),
            "vulnerabilities_by_severity": by_severity,
            "security_score": dependency_analyzer._calculate_security_score(vulnerabilities),
            "recommendations": [
                f"Update {vuln.package} from {vuln.installed_version} to {vuln.fixed_version}"
                for vuln in vulnerabilities if vuln.fixed_version
            ]
        }
        
    except Exception as e:
        logging.error(f"Vulnerability scanning failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_path": project_path
        }


@mcp.tool()
async def check_licenses(project_path: str, allowed_licenses: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Check license compliance for project dependencies.
    
    Args:
        project_path: Root path of the project
        allowed_licenses: List of allowed license types
    
    Returns:
        Dictionary containing license compliance analysis
    """
    try:
        logging.info(f"Checking license compliance in: {project_path}")
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"Project path not found: {project_path}"
            }
        
        # Default allowed licenses if not specified
        if allowed_licenses is None:
            allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause", "ISC"]
        
        licenses = await dependency_analyzer.license_analyzer.analyze_python_licenses(project_path)
        compliance = dependency_analyzer.license_analyzer.check_license_compatibility(licenses, allowed_licenses)
        
        return {
            "success": True,
            "project_path": project_path,
            "allowed_licenses": allowed_licenses,
            "license_analysis": compliance,
            "recommendations": [
                f"Review license for {pkg['package']}: {pkg['license']}"
                for pkg in compliance["incompatible"]
            ] + [
                f"Clarify license for {pkg['package']}"
                for pkg in compliance["unknown"]
            ]
        }
        
    except Exception as e:
        logging.error(f"License checking failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_path": project_path
        }


@mcp.tool()
async def find_unused_dependencies(project_path: str, language: str = "auto") -> Dict[str, Any]:
    """
    Find dependencies that appear to be unused.
    
    Args:
        project_path: Root path of the project
        language: Programming language ("python", "javascript", "auto")
    
    Returns:
        Dictionary containing unused dependency analysis
    """
    try:
        logging.info(f"Finding unused dependencies in: {project_path}")
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"Project path not found: {project_path}"
            }
        
        # Detect language if auto
        if language == "auto":
            language = dependency_analyzer._detect_project_language(project_path)
        
        unused = await dependency_analyzer._find_unused_dependencies(project_path, language)
        
        return {
            "success": True,
            "project_path": project_path,
            "language": language,
            "unused_dependencies": unused,
            "count": len(unused),
            "recommendations": [
                f"Consider removing unused dependency: {dep}"
                for dep in unused
            ] if unused else ["All dependencies appear to be in use"]
        }
        
    except Exception as e:
        logging.error(f"Unused dependency analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_path": project_path
        }


@mcp.tool()
async def analyze_version_conflicts(project_path: str, language: str = "auto") -> Dict[str, Any]:
    """
    Analyze version conflicts and compatibility issues.
    
    Args:
        project_path: Root path of the project
        language: Programming language ("python", "javascript", "auto")
    
    Returns:
        Dictionary containing version conflict analysis
    """
    try:
        logging.info(f"Analyzing version conflicts in: {project_path}")
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"Project path not found: {project_path}"
            }
        
        # Detect language if auto
        if language == "auto":
            language = dependency_analyzer._detect_project_language(project_path)
        
        conflicts = []
        
        if language == "python":
            # Use pip check to find conflicts
            result = await dependency_analyzer.security_scanner.run_command([
                "pip", "check"
            ], cwd=project_path)
            
            if not result["success"] and result["stdout"]:
                # Parse pip check output for conflicts
                for line in result["stdout"].split('\n'):
                    if "has requirement" in line:
                        conflicts.append(line.strip())
        
        return {
            "success": True,
            "project_path": project_path,
            "language": language,
            "conflicts": conflicts,
            "has_conflicts": len(conflicts) > 0,
            "recommendations": [
                "Review and resolve version conflicts",
                "Consider using dependency resolution tools",
                "Update conflicting packages to compatible versions"
            ] if conflicts else ["No version conflicts detected"]
        }
        
    except Exception as e:
        logging.error(f"Version conflict analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_path": project_path
        }


@mcp.tool()
async def suggest_updates(project_path: str, risk_level: str = "medium") -> Dict[str, Any]:
    """
    Suggest dependency updates based on risk tolerance.
    
    Args:
        project_path: Root path of the project
        risk_level: Maximum risk level for updates ("low", "medium", "high")
    
    Returns:
        Dictionary containing update suggestions
    """
    try:
        logging.info(f"Suggesting updates for: {project_path}")
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"Project path not found: {project_path}"
            }
        
        language = dependency_analyzer._detect_project_language(project_path)
        updates = await dependency_analyzer._analyze_available_updates(project_path, language)
        
        # Filter by risk level
        risk_order = {"low": 0, "medium": 1, "high": 2}
        max_risk = risk_order.get(risk_level, 1)
        
        safe_updates = [
            update for update in updates
            if risk_order.get(update.risk_level, 2) <= max_risk
        ]
        
        return {
            "success": True,
            "project_path": project_path,
            "risk_level": risk_level,
            "total_updates_available": len(updates),
            "safe_updates": [
                {
                    "package": update.package,
                    "current_version": update.current_version,
                    "latest_version": update.latest_version,
                    "update_type": update.update_type,
                    "risk_level": update.risk_level,
                    "breaking_changes": update.breaking_changes
                }
                for update in safe_updates
            ],
            "update_commands": [
                f"pip install --upgrade {update.package}=={update.latest_version}"
                for update in safe_updates
            ] if language == "python" else [],
            "recommendations": [
                f"Safe to update {update.package} from {update.current_version} to {update.latest_version}"
                for update in safe_updates
            ]
        }
        
    except Exception as e:
        logging.error(f"Update suggestion failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_path": project_path
        }


@mcp.tool()
async def comprehensive_dependency_analysis(project_path: str, language: str = "auto") -> Dict[str, Any]:
    """
    Perform comprehensive dependency analysis including security, licenses, and updates.
    
    Args:
        project_path: Root path of the project
        language: Programming language ("python", "javascript", "auto")
    
    Returns:
        Dictionary containing comprehensive dependency analysis
    """
    try:
        logging.info(f"Performing comprehensive dependency analysis: {project_path}")
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"Project path not found: {project_path}"
            }
        
        analysis = await dependency_analyzer.analyze_project_dependencies(project_path, language)
        
        return {
            "success": True,
            "analysis": analysis,
            "action_items": [
                f"Address {len(analysis['vulnerabilities'])} security vulnerabilities",
                f"Review {len(analysis['updates'])} available updates",
                f"Consider removing {len(analysis['unused_dependencies'])} unused dependencies"
            ],
            "priority_actions": [
                vuln for vuln in analysis.get("vulnerabilities", [])
                if vuln.severity in ["critical", "high"]
            ]
        }
        
    except Exception as e:
        logging.error(f"Comprehensive dependency analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_path": project_path
        }


def main():
    """Main entry point for the MCP server"""
    setup_logging()
    logging.info("Starting Dependency Analysis MCP Server")
    
    try:
        # Run the MCP server
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logging.info("Server interrupted by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()