import os
import subprocess
import psutil # This was the missing dependency
import platform
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
# Trying a more explicit import path for settings
from ClaudeDesktopBridge.app.utils.logger import setup_logger
from ClaudeDesktopBridge.app.utils.config import settings

# Setup logger
logger = setup_logger(__name__)

class SystemModule:
    def __init__(self):
        self.os_type = platform.system()
        # These lines were causing AttributeError if settings object was not correctly loaded/populated
        self.allowed_apps = settings.ALLOWED_APPS 
        self.allowed_commands = settings.ALLOWED_COMMANDS
    
    def execute_command(self, command: str, timeout: Optional[int] = None, shell: bool = True) -> Dict[str, Any]:
        """Execute a system command with security checks"""
        try:
            # Security check - only allow specific commands
            command_base = command.split()[0].lower() if command else ""
            # Ensure allowed_commands is populated
            if not hasattr(self, 'allowed_commands') or self.allowed_commands is None:
                 logger.error("ALLOWED_COMMANDS not initialized in SystemModule. Denying all commands.")
                 raise ValueError("Command execution policy not configured. Operation denied.")

            if command_base not in self.allowed_commands:
                logger.warning(f"Disallowed command attempted: {command_base}. Full command: {command}")
                raise ValueError(f"Command '{command_base}' is not allowed. Allowed commands: {', '.join(self.allowed_commands)}")
            
            logger.info(f"Executing command: {command}")
            
            result = subprocess.run(
                command,
                shell=shell, # Security Note: shell=True can be risky if command string is not sanitized
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False # Do not raise CalledProcessError, handle return code manually
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout} seconds: {command}")
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds", # Added error field for clarity
                "stdout": "",
                "stderr": "Timeout expired",
                "return_code": -1 
            }
        except ValueError as ve: # Catch our disallowed command error
            logger.warning(f"Command execution denied: {str(ve)}")
            return {
                "success": False,
                "error": str(ve),
                "stdout": "",
                "stderr": str(ve),
                "return_code": -1
            }
        except Exception as e:
            logger.error(f"Error executing command '{command}': {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }
    
    def launch_application(self, app_name: str) -> Dict[str, Any]:
        """Launch an application with security checks"""
        try:
            if not hasattr(self, 'allowed_apps') or self.allowed_apps is None:
                 logger.error("ALLOWED_APPS not initialized in SystemModule. Denying all app launches.")
                 raise ValueError("Application launch policy not configured. Operation denied.")

            if app_name not in self.allowed_apps:
                raise ValueError(f"Application '{app_name}' is not allowed. Allowed applications: {', '.join(self.allowed_apps)}")
            
            logger.info(f"Launching application: {app_name}")
            
            if self.os_type == "Windows":
                subprocess.Popen(["start", app_name], shell=True) # No result check, fire and forget
            elif self.os_type == "Darwin":
                subprocess.Popen(["open", "-a", app_name])
            elif self.os_type == "Linux":
                subprocess.Popen([app_name]) # Assumes app_name is in PATH
            else:
                raise ValueError(f"Unsupported OS: {self.os_type}")
            
            return {"success": True, "message": f"Launched {app_name}"}
        
        except Exception as e:
            logger.error(f"Error launching application '{app_name}': {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def list_applications(self) -> Dict[str, Any]:
        # Implementation can be complex and OS-dependent, providing a placeholder
        logger.info("Listing installed applications (placeholder implementation)")
        return {
            "success": True, 
            "applications": [{"name": "PlaceholderApp", "version": "1.0"}], 
            "count": 1,
            "message": "Note: This is a placeholder implementation for list_applications."
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        logger.info("Getting system information")
        try:
            return {
                "success": True,
                "cpu": {"count": psutil.cpu_count(logical=True), "usage_percent": psutil.cpu_percent(interval=0.1)},
                "memory": {"total": psutil.virtual_memory().total, "available": psutil.virtual_memory().available, "percent": psutil.virtual_memory().percent},
                "disk": {"total": psutil.disk_usage('/').total, "used": psutil.disk_usage('/').used, "free": psutil.disk_usage('/').free, "percent": psutil.disk_usage('/').percent},
                "platform": {"system": platform.system(), "release": platform.release(), "version": platform.version()}
            }
        except Exception as e:
            logger.error(f"Error getting system information: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def get_running_processes(self) -> Dict[str, Any]:
        logger.info("Getting running processes")
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            processes.sort(key=lambda x: x.get('memory_percent', 0) or 0, reverse=True) # ensure memory_percent exists
            return {"success": True, "processes": processes, "count": len(processes)}
        except Exception as e:
            logger.error(f"Error getting running processes: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e), "processes": [], "count": 0}
