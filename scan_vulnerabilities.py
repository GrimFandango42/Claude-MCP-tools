#!/usr/bin/env python3
"""
Security vulnerability scanner for MCP servers.
Scans Python dependencies for known vulnerabilities.
"""

import json
import subprocess
import sys
from pathlib import Path
import re

def run_safety_check(packages):
    """Run safety check on a list of packages."""
    try:
        # Create a temporary requirements file
        temp_req = Path("temp_requirements.txt")
        with open(temp_req, "w") as f:
            for pkg in packages:
                f.write(f"{pkg}\n")
        
        # Run safety check
        result = subprocess.run([
            sys.executable, "-m", "safety", "check", 
            "--file", str(temp_req), "--json"
        ], capture_output=True, text=True)
        
        # Clean up
        temp_req.unlink()
        
        if result.stdout:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"Safety check failed: {e}")
        return []

def parse_requirements(file_path):
    """Parse requirements from requirements.txt or pyproject.toml."""
    packages = []
    
    if file_path.suffix == ".txt":
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract package name and version
                    match = re.match(r"([a-zA-Z0-9_-]+)([>=<!=]*.*)?", line)
                    if match:
                        packages.append(line)
    
    elif file_path.suffix == ".toml":
        with open(file_path) as f:
            content = f.read()
            # Extract dependencies from pyproject.toml
            deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if deps_match:
                deps_str = deps_match.group(1)
                for line in deps_str.split(','):
                    line = line.strip().strip('"').strip("'")
                    if line and not line.startswith("#"):
                        packages.append(line)
    
    return packages

def scan_server_directory(server_path):
    """Scan a server directory for vulnerabilities."""
    server_path = Path(server_path)
    results = {"server": server_path.name, "vulnerabilities": []}
    
    # Find requirements files
    req_files = list(server_path.glob("requirements.txt")) + list(server_path.glob("pyproject.toml"))
    
    for req_file in req_files:
        print(f"Scanning {req_file}")
        packages = parse_requirements(req_file)
        
        if packages:
            vulnerabilities = run_safety_check(packages)
            if vulnerabilities:
                results["vulnerabilities"].extend(vulnerabilities)
                print(f"  Found {len(vulnerabilities)} vulnerabilities")
            else:
                print(f"  No vulnerabilities found")
        else:
            print(f"  No packages found to scan")
    
    return results

def main():
    """Main function to scan all servers."""
    servers_dir = Path("servers")
    all_results = []
    
    print("Security Vulnerability Scanner for MCP Servers")
    print("="*50)
    
    for server_dir in servers_dir.iterdir():
        if server_dir.is_dir():
            print(f"\nScanning {server_dir.name}...")
            results = scan_server_directory(server_dir)
            all_results.append(results)
    
    # Summary
    print("\nVULNERABILITY SCAN RESULTS")
    print("="*50)
    
    total_vulns = 0
    for result in all_results:
        vulns = len(result["vulnerabilities"])
        total_vulns += vulns
        if vulns > 0:
            print(f"VULNERABLE {result['server']}: {vulns} vulnerabilities")
            for vuln in result["vulnerabilities"]:
                pkg = vuln.get("package", "unknown")
                cve = vuln.get("cve", "N/A") 
                severity = vuln.get("severity", "unknown")
                print(f"   - {pkg}: {cve} (Severity: {severity})")
        else:
            print(f"SECURE {result['server']}: No vulnerabilities")
    
    print(f"\nTotal vulnerabilities found: {total_vulns}")
    
    # Save detailed results
    with open("vulnerability_scan_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"Detailed results saved to: vulnerability_scan_results.json")

if __name__ == "__main__":
    main()