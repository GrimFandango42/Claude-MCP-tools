#!/usr/bin/env python3
"""
Quick validation script to check if all required files are present
for the Containerized Computer Use MCP server.
"""

import os
from pathlib import Path
import sys

def check_files():
    """Check if all required files exist."""
    
    base_dir = Path(__file__).parent
    
    required_files = [
        # Core server files
        "containerized_mcp_server.py",
        "computer_use_container.py",
        "container_mcp_wrapper.py",
        "requirements.txt",
        
        # Docker files
        "Dockerfile",
        "docker-compose.yml",
        "startup.sh",
        "supervisord.conf",
        
        # Launch and test files
        "launch_containerized_mcp.bat",
        "test_complete_server.py",
        "run_tests.bat",
        "build_docker.bat",
        
        # Documentation
        "README.md",
        "DEPLOYMENT_GUIDE.md",
        
        # Directories
        "shared",
        "workspaces"
    ]
    
    missing_files = []
    
    print("Checking required files...")
    print("=" * 50)
    
    for file in required_files:
        file_path = base_dir / file
        if file_path.exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            missing_files.append(file)
    
    print("=" * 50)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    else:
        print("\n✅ All required files present!")
        return True

def check_docker():
    """Check if Docker is available."""
    print("\nChecking Docker...")
    print("=" * 50)
    
    try:
        import subprocess
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Docker installed: {result.stdout.strip()}")
            
            # Check if Docker daemon is running
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Docker daemon is running")
                return True
            else:
                print("✗ Docker daemon is not running - start Docker Desktop")
                return False
        else:
            print("✗ Docker not found - install Docker Desktop")
            return False
    except Exception as e:
        print(f"✗ Error checking Docker: {e}")
        return False

def check_python_deps():
    """Check if Python dependencies can be installed."""
    print("\nChecking Python environment...")
    print("=" * 50)
    
    try:
        import mcp
        print("✓ MCP framework is installed")
        return True
    except ImportError:
        print("✗ MCP framework not installed - run 'pip install -r requirements.txt'")
        return False

def main():
    """Run all checks."""
    print("Containerized Computer Use MCP - Pre-deployment Validation")
    print("=" * 50)
    
    files_ok = check_files()
    docker_ok = check_docker()
    python_ok = check_python_deps()
    
    print("\n" + "=" * 50)
    print("Validation Summary:")
    print("=" * 50)
    print(f"Files: {'✅ PASS' if files_ok else '❌ FAIL'}")
    print(f"Docker: {'✅ PASS' if docker_ok else '❌ FAIL'}")
    print(f"Python: {'✅ PASS' if python_ok else '❌ FAIL'}")
    
    if all([files_ok, docker_ok, python_ok]):
        print("\n✅ System ready for deployment!")
        print("\nNext steps:")
        print("1. Run: .\\build_docker.bat")
        print("2. Run: .\\run_tests.bat")
        print("3. Add to Claude Desktop configuration")
    else:
        print("\n❌ System not ready - fix issues above")
        
    return 0 if all([files_ok, docker_ok, python_ok]) else 1

if __name__ == "__main__":
    sys.exit(main())
