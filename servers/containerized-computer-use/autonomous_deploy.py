#!/usr/bin/env python3
"""
Autonomous Deployment Script for Containerized Computer Use MCP
This script will perform all deployment steps that can be done without human intervention.
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('autonomous_deploy.log')
    ]
)

class AutonomousDeployer:
    """Handles autonomous deployment of Containerized Computer Use MCP."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.results = {
            "steps_completed": [],
            "steps_failed": [],
            "needs_human": []
        }
        
    def log_step(self, step: str, success: bool, details: str = ""):
        """Log deployment step result."""
        emoji = "✅" if success else "❌"
        logging.info(f"{emoji} {step}: {details}")
        
        if success:
            self.results["steps_completed"].append(step)
        else:
            self.results["steps_failed"].append(f"{step}: {details}")
    
    def run_command(self, cmd: List[str], cwd: str = None) -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd or self.base_dir,
                timeout=300  # 5 minute timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    async def check_docker_status(self) -> bool:
        """Check if Docker is running."""
        logging.info("\n=== Checking Docker Status ===")
        
        success, output = self.run_command(["docker", "ps"])
        if success:
            self.log_step("Docker check", True, "Docker is running")
            return True
        else:
            self.log_step("Docker check", False, "Docker Desktop not running")
            self.results["needs_human"].append("Start Docker Desktop")
            return False
    
    async def validate_files(self) -> bool:
        """Validate all required files exist."""
        logging.info("\n=== Validating Files ===")
        
        success, output = self.run_command(
            [sys.executable, "validate_setup.py"]
        )
        
        if "All required files present!" in output:
            self.log_step("File validation", True, "All files present")
            return True
        else:
            self.log_step("File validation", False, "Missing files")
            return False
    
    async def build_docker_image(self) -> bool:
        """Build the Docker image."""
        logging.info("\n=== Building Docker Image ===")
        
        # Check if image already exists
        success, output = self.run_command(
            ["docker", "images", "-q", "containerized-computer-use:latest"]
        )
        
        if success and output.strip():
            logging.info("Docker image already exists, skipping build")
            self.log_step("Docker image check", True, "Image exists")
            return True
        
        # Build the image
        logging.info("Building Docker image (this may take 5-10 minutes)...")
        success, output = self.run_command(
            ["docker-compose", "build", "--no-cache"]
        )
        
        if success:
            self.log_step("Docker build", True, "Image built successfully")
            return True
        else:
            self.log_step("Docker build", False, output[-500:])  # Last 500 chars
            return False
    
    async def start_container(self) -> bool:
        """Start the Docker container."""
        logging.info("\n=== Starting Container ===")
        
        # Check if container exists
        success, output = self.run_command(
            ["docker", "ps", "-a", "--filter", "name=windows-computer-use", "--format", "{{.Names}}"]
        )
        
        if "windows-computer-use" in output:
            # Container exists, check if running
            success, output = self.run_command(
                ["docker", "ps", "--filter", "name=windows-computer-use", "--format", "{{.Names}}"]
            )
            
            if "windows-computer-use" in output:
                self.log_step("Container status", True, "Already running")
                return True
            else:
                # Start existing container
                success, output = self.run_command(
                    ["docker", "start", "windows-computer-use"]
                )
                if success:
                    self.log_step("Container start", True, "Started existing container")
                    return True
        
        # Create new container
        success, output = self.run_command(
            ["docker-compose", "up", "-d"]
        )
        
        if success:
            self.log_step("Container creation", True, "Container started")
            # Wait for services to initialize
            logging.info("Waiting 10 seconds for services to initialize...")
            await asyncio.sleep(10)
            return True
        else:
            self.log_step("Container creation", False, output[-500:])
            return False
    
    async def test_container(self) -> bool:
        """Test container functionality."""
        logging.info("\n=== Testing Container ===")
        
        # Test 1: Container is running
        success, output = self.run_command(
            ["docker", "ps", "--filter", "name=windows-computer-use", "--format", "{{.Status}}"]
        )
        
        if not success or "Up" not in output:
            self.log_step("Container running test", False, "Container not running")
            return False
        else:
            self.log_step("Container running test", True, output.strip())
        
        # Test 2: Execute command in container
        success, output = self.run_command(
            ["docker", "exec", "windows-computer-use", "python3", "-c", "print('Container test successful!')"]
        )
        
        if success and "Container test successful!" in output:
            self.log_step("Container exec test", True, "Python execution works")
        else:
            self.log_step("Container exec test", False, "Cannot execute Python in container")
            return False
        
        # Test 3: Check VNC is running
        success, output = self.run_command(
            ["docker", "exec", "windows-computer-use", "ps", "aux"]
        )
        
        if success and "x11vnc" in output:
            self.log_step("VNC service test", True, "VNC is running")
        else:
            self.log_step("VNC service test", False, "VNC not running")
        
        return True
    
    async def run_mcp_tests(self) -> bool:
        """Run MCP server tests."""
        logging.info("\n=== Running MCP Tests ===")
        
        # Create virtual environment if needed
        venv_path = self.base_dir / ".venv"
        if not venv_path.exists():
            logging.info("Creating virtual environment...")
            success, output = self.run_command(
                [sys.executable, "-m", "venv", ".venv"]
            )
            if not success:
                self.log_step("Virtual environment creation", False, output)
                return False
        
        # Install dependencies
        pip_path = venv_path / "Scripts" / "pip.exe"
        if not pip_path.exists():
            pip_path = venv_path / "bin" / "pip"
        
        logging.info("Installing dependencies...")
        success, output = self.run_command(
            [str(pip_path), "install", "-r", "requirements.txt"]
        )
        
        if not success:
            self.log_step("Dependency installation", False, "Failed to install dependencies")
            return False
        
        # Run tests
        python_path = venv_path / "Scripts" / "python.exe"
        if not python_path.exists():
            python_path = venv_path / "bin" / "python"
        
        success, output = self.run_command(
            [str(python_path), "test_complete_server.py"]
        )
        
        if success and "All tests passed!" in output:
            self.log_step("MCP tests", True, "All tests passed")
            return True
        else:
            self.log_step("MCP tests", False, "Some tests failed")
            # Log specific failures
            for line in output.split('\n'):
                if "FAILED" in line:
                    logging.error(f"  {line}")
            return False
    
    async def update_claude_config(self) -> bool:
        """Update Claude Desktop configuration."""
        logging.info("\n=== Updating Claude Desktop Configuration ===")
        
        config_path = Path(r"C:\Users\Nithin\AppData\Roaming\Claude\claude_desktop_config.json")
        
        try:
            # Read current config
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check if already configured
            if "containerized-computer-use" in config.get("mcpServers", {}):
                self.log_step("Config check", True, "Already configured")
                return True
            
            # Add new server config
            new_server = {
                "command": "cmd",
                "args": ["/c", f"{self.base_dir}\\launch_containerized_mcp.bat"],
                "cwd": str(self.base_dir),
                "keepAlive": True,
                "stderrToConsole": True,
                "description": "Containerized Computer Use with Docker isolation and VNC access"
            }
            
            config["mcpServers"]["containerized-computer-use"] = new_server
            
            # Backup current config
            backup_path = config_path.with_suffix('.json.bak')
            with open(backup_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Write updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.log_step("Config update", True, "Configuration updated")
            self.results["needs_human"].append("Restart Claude Desktop to apply changes")
            return True
            
        except Exception as e:
            self.log_step("Config update", False, str(e))
            return False
    
    async def attempt_claude_restart(self) -> bool:
        """Attempt to restart Claude Desktop using Windows Computer Use."""
        logging.info("\n=== Attempting Claude Desktop Restart ===")
        
        try:
            # This would use the Windows Computer Use MCP if we had access
            # For now, we'll just note that human intervention is needed
            self.results["needs_human"].append("Restart Claude Desktop manually")
            self.log_step("Claude restart", False, "Manual restart required")
            return False
            
        except Exception as e:
            self.log_step("Claude restart", False, str(e))
            return False
    
    async def run_autonomous_deployment(self):
        """Run the complete autonomous deployment process."""
        logging.info("Starting Autonomous Deployment of Containerized Computer Use MCP")
        logging.info("=" * 70)
        
        # Step 1: Validate prerequisites
        docker_ok = await self.check_docker_status()
        if not docker_ok:
            logging.warning("Docker not running - cannot proceed with deployment")
            return
        
        files_ok = await self.validate_files()
        if not files_ok:
            logging.error("File validation failed - fix issues before proceeding")
            return
        
        # Step 2: Build and deploy
        build_ok = await self.build_docker_image()
        if not build_ok:
            logging.error("Docker build failed - check logs for details")
            return
        
        # Step 3: Start container
        container_ok = await self.start_container()
        if not container_ok:
            logging.error("Container start failed")
            return
        
        # Step 4: Test container
        test_ok = await self.test_container()
        if not test_ok:
            logging.warning("Container tests failed - container may not be fully functional")
        
        # Step 5: Run MCP tests
        mcp_ok = await self.run_mcp_tests()
        if not mcp_ok:
            logging.warning("MCP tests failed - server may not work properly")
        
        # Step 6: Update configuration
        config_ok = await self.update_claude_config()
        
        # Step 7: Attempt restart (will fail, needs human)
        restart_ok = await self.attempt_claude_restart()
        
        # Generate summary report
        await self.generate_report()
    
    async def generate_report(self):
        """Generate deployment summary report."""
        logging.info("\n" + "=" * 70)
        logging.info("DEPLOYMENT SUMMARY")
        logging.info("=" * 70)
        
        # Completed steps
        logging.info(f"\n✅ Completed Steps ({len(self.results['steps_completed'])}):")
        for step in self.results["steps_completed"]:
            logging.info(f"  • {step}")
        
        # Failed steps
        if self.results["steps_failed"]:
            logging.info(f"\n❌ Failed Steps ({len(self.results['steps_failed'])}):")
            for step in self.results["steps_failed"]:
                logging.info(f"  • {step}")
        
        # Human actions needed
        if self.results["needs_human"]:
            logging.info(f"\n👤 Human Actions Required ({len(self.results['needs_human'])}):")
            for action in self.results["needs_human"]:
                logging.info(f"  • {action}")
        
        # Overall status
        total_steps = len(self.results["steps_completed"]) + len(self.results["steps_failed"])
        success_rate = (len(self.results["steps_completed"]) / total_steps * 100) if total_steps > 0 else 0
        
        logging.info(f"\n📊 Overall Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            logging.info("\n✅ DEPLOYMENT SUCCESSFUL!")
            logging.info("\nContainer Details:")
            logging.info("  • Name: windows-computer-use")
            logging.info("  • VNC: vnc://localhost:5900")
            logging.info("  • Password: vnc123")
            logging.info("\nNext Steps:")
            logging.info("  1. Restart Claude Desktop")
            logging.info("  2. Test with: 'Take a screenshot using the containerized computer'")
        else:
            logging.info("\n❌ DEPLOYMENT NEEDS ATTENTION")
            logging.info("Review failed steps and try again")
        
        # Save report
        report_path = self.base_dir / "deployment_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        logging.info(f"\nDetailed report saved to: {report_path}")


async def main():
    """Run autonomous deployment."""
    deployer = AutonomousDeployer()
    await deployer.run_autonomous_deployment()


if __name__ == "__main__":
    asyncio.run(main())
