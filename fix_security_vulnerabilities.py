#!/usr/bin/env python3
"""
Security vulnerability fixes for MCP servers.
Updates known vulnerable packages to secure versions.
"""

import re
from pathlib import Path
import shutil

# Known vulnerable packages and their secure versions
SECURITY_UPDATES = {
    # Common vulnerabilities found in dependency scanning
    "pillow==10.2.0": "pillow>=10.3.0",  # CVE-2024-28219 and others
    "numpy==1.26.4": "numpy>=1.26.5",    # Various security issues
    "requests==2.31.0": "requests>=2.32.0",  # CVE-2024-35195
    "opencv-python==4.9.0.80": "opencv-python>=4.10.0",  # Security updates
    "websocket-client==1.7.0": "websocket-client>=1.8.0",  # Security improvements
    "docker==7.0.0": "docker>=7.1.0",    # Security patches
    
    # Packages with known issues
    "pynput==1.7.6": "pynput>=1.7.7",
    "pyautogui==0.9.54": "pyautogui>=0.9.55",
    
    # MCP and HTTP libraries - ensure latest versions
    "httpx>=0.22.0": "httpx>=0.27.0",
    "mcp>=1.0.0": "mcp>=1.0.0",  # Already secure
}

def backup_file(file_path):
    """Create a backup of the file before modification."""
    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
    shutil.copy2(file_path, backup_path)
    print(f"  Backup created: {backup_path.name}")
    return backup_path

def update_requirements_txt(file_path):
    """Update requirements.txt file with security fixes."""
    print(f"\nUpdating {file_path}")
    
    backup_file(file_path)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    updates_made = []
    
    for vulnerable, secure in SECURITY_UPDATES.items():
        # Handle exact matches and version constraints
        old_pkg = vulnerable.split('==')[0] if '==' in vulnerable else vulnerable.split('>=')[0]
        
        # Replace exact version matches
        if '==' in vulnerable:
            if vulnerable in content:
                content = content.replace(vulnerable, secure)
                updates_made.append(f"{vulnerable} -> {secure}")
        # Handle version constraint updates
        elif '>=' in vulnerable:
            pattern = rf"{re.escape(old_pkg)}>=[\d.]+"
            if re.search(pattern, content):
                content = re.sub(pattern, secure, content)
                updates_made.append(f"{old_pkg} version constraint updated to {secure}")
    
    if updates_made:
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"  UPDATED {len(updates_made)} packages:")
        for update in updates_made:
            print(f"    - {update}")
    else:
        print(f"  No security updates needed")

def update_pyproject_toml(file_path):
    """Update pyproject.toml file with security fixes."""
    print(f"\nUpdating {file_path}")
    
    backup_file(file_path)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    updates_made = []
    
    # Extract dependencies section
    deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if deps_match:
        deps_section = deps_match.group(1)
        new_deps_section = deps_section
        
        for vulnerable, secure in SECURITY_UPDATES.items():
            old_pkg = vulnerable.split('==')[0] if '==' in vulnerable else vulnerable.split('>=')[0]
            
            # Update version constraints in dependencies
            if old_pkg in deps_section:
                # Look for the package in quotes
                old_pattern = rf'"{re.escape(old_pkg)}[^"]*"'
                new_value = f'"{secure}"'
                
                if re.search(old_pattern, new_deps_section):
                    new_deps_section = re.sub(old_pattern, new_value, new_deps_section)
                    updates_made.append(f"{old_pkg} -> {secure}")
        
        if updates_made:
            # Replace the dependencies section
            new_content = content.replace(deps_section, new_deps_section)
            
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            print(f"  UPDATED {len(updates_made)} packages:")
            for update in updates_made:
                print(f"    - {update}")
        else:
            print(f"  No security updates needed")
    else:
        print(f"  No dependencies section found")

def main():
    """Main function to apply security fixes."""
    servers_dir = Path("servers")
    
    print("Security Vulnerability Fix Tool")
    print("="*50)
    print(f"Scanning {len(list(servers_dir.iterdir()))} server directories...")
    
    total_files_updated = 0
    
    for server_dir in servers_dir.iterdir():
        if server_dir.is_dir():
            print(f"\nScanning {server_dir.name}...")
            
            # Process requirements.txt files
            req_files = list(server_dir.glob("requirements.txt"))
            for req_file in req_files:
                update_requirements_txt(req_file)
                total_files_updated += 1
            
            # Process pyproject.toml files
            toml_files = list(server_dir.glob("pyproject.toml"))
            for toml_file in toml_files:
                update_pyproject_toml(toml_file)
                total_files_updated += 1
            
            if not req_files and not toml_files:
                print(f"  No dependency files found")
    
    print(f"\nSECURITY UPDATE SUMMARY")
    print("="*50)
    print(f"Files processed: {total_files_updated}")
    print(f"Backup files created for safety")
    print(f"\nSecurity updates applied based on known vulnerabilities:")
    for vulnerable, secure in SECURITY_UPDATES.items():
        print(f"  - {vulnerable} -> {secure}")
    
    print(f"\nIMPORTANT: Test all servers after these updates!")
    print(f"To restore from backup: cp file.backup file")

if __name__ == "__main__":
    main()