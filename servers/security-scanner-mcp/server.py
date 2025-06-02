"""
Security Scanner MCP Server
Focuses on what Claude can't do - check actual vulnerabilities
"""

from fastmcp import FastMCP
import subprocess
import json
from pathlib import Path

mcp = FastMCP("security-scanner")

@mcp.tool()
async def scan_python_deps(project_path: str) -> dict:
    """
    Scan Python dependencies for known vulnerabilities using pip-audit.
    """
    try:
        result = subprocess.run(
            ["pip-audit", "--format", "json"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                "status": "success",
                "vulnerabilities": data.get("vulnerabilities", []),
                "summary": f"Found {len(data.get('vulnerabilities', []))} vulnerabilities"
            }
        else:
            return {
                "status": "error",
                "message": result.stderr
            }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"pip-audit not installed or error: {str(e)}"
        }

@mcp.tool()
async def scan_node_deps(project_path: str) -> dict:
    """
    Scan Node.js dependencies using npm audit.
    """
    try:
        result = subprocess.run(
            ["npm", "audit", "--json"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        data = json.loads(result.stdout)
        vulnerabilities = data.get("vulnerabilities", {})
        
        return {
            "status": "success",
            "vulnerabilities": len(vulnerabilities),
            "severity": {
                "high": sum(1 for v in vulnerabilities.values() if v.get("severity") == "high"),
                "medium": sum(1 for v in vulnerabilities.values() if v.get("severity") == "medium"),
                "low": sum(1 for v in vulnerabilities.values() if v.get("severity") == "low")
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"npm audit failed: {str(e)}"
        }

@mcp.tool()
async def check_licenses(project_path: str) -> dict:
    """
    Check licenses of dependencies for compliance issues.
    """
    # Simple implementation - can be enhanced with pip-licenses or license-checker
    problematic_licenses = ["GPL", "AGPL", "LGPL"]  # For proprietary projects
    
    try:
        # Check Python
        result = subprocess.run(
            ["pip-licenses", "--format=json"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            licenses = json.loads(result.stdout)
            issues = [
                pkg for pkg in licenses 
                if any(lic in pkg.get("License", "") for lic in problematic_licenses)
            ]
            
            return {
                "status": "success",
                "total_packages": len(licenses),
                "license_issues": issues,
                "summary": f"{len(issues)} packages with potential license conflicts"
            }
    except:
        pass
    
    return {
        "status": "partial",
        "message": "License checking requires pip-licenses or similar tools"
    }

@mcp.tool()
async def security_scan(project_path: str) -> dict:
    """
    Run all available security scans on a project.
    """
    results = {}
    
    # Detect project type
    path = Path(project_path)
    if (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
        results["python"] = await scan_python_deps(project_path)
    
    if (path / "package.json").exists():
        results["node"] = await scan_node_deps(project_path)
    
    results["licenses"] = await check_licenses(project_path)
    
    return results

if __name__ == "__main__":
    mcp.run(transport="stdio")