import os
import subprocess
import psutil
import platform
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from app.utils.logger import setup_logger
from app.utils.config import settings

# Setup logger
logger = setup_logger(__name__)

class SystemModule:
    def __init__(self):
        self.os_type = platform.system()
        self.allowed_apps = settings.ALLOWED_APPS
        self.allowed_commands = settings.ALLOWED_COMMANDS
    
    def execute_command(self, command: str, timeout: Optional[int] = None, shell: bool = True) -> Dict[str, Any]:
        """Execute a system command with security checks"""
        try:
            # Security check - only allow specific commands
            command_base = command.split()[0].lower() if command else ""
            if command_base not in self.allowed_commands:
                raise ValueError(f"Command '{command_base}' is not allowed. Allowed commands: {', '.join(self.allowed_commands)}")
            
            logger.info(f"Executing command: {command}")
            
            # Execute command
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Prepare response
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout} seconds: {command}")
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "stdout": "",
                "stderr": "Timeout expired",
                "return_code": -1
            }
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}", exc_info=True)
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
            # Security check - only allow specific applications
            if app_name not in self.allowed_apps:
                raise ValueError(f"Application '{app_name}' is not allowed. Allowed applications: {', '.join(self.allowed_apps)}")
            
            logger.info(f"Launching application: {app_name}")
            
            # Launch application based on OS
            if self.os_type == "Windows":
                # On Windows, use start command
                result = subprocess.Popen(
                    ["start", app_name],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                return {"success": True, "message": f"Launched {app_name}"}
            
            elif self.os_type == "Darwin":  # macOS
                # On macOS, use open command
                result = subprocess.Popen(
                    ["open", "-a", app_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                return {"success": True, "message": f"Launched {app_name}"}
            
            elif self.os_type == "Linux":
                # On Linux, just run the command
                result = subprocess.Popen(
                    [app_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                return {"success": True, "message": f"Launched {app_name}"}
            
            else:
                raise ValueError(f"Unsupported OS: {self.os_type}")
        
        except Exception as e:
            logger.error(f"Error launching application: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def list_applications(self) -> Dict[str, Any]:
        """List installed applications"""
        try:
            logger.info("Listing installed applications")
            
            applications = []
            
            # List applications based on OS
            if self.os_type == "Windows":
                # On Windows, use PowerShell to get installed apps
                command = "powershell -command \"Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion | ConvertTo-Json\""
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        apps_data = json.loads(result.stdout)
                        
                        # Handle case where only one app is returned (not in a list)
                        if isinstance(apps_data, dict):
                            apps_data = [apps_data]
                        
                        for app in apps_data:
                            if "DisplayName" in app and app["DisplayName"]:
                                applications.append({
                                    "name": app["DisplayName"],
                                    "version": app.get("DisplayVersion", "")
                                })
                    except json.JSONDecodeError:
                        logger.error(f"Error parsing JSON from PowerShell output: {result.stdout}")
            
            elif self.os_type == "Darwin":  # macOS
                # On macOS, list applications in /Applications
                command = "ls -la /Applications | grep \".app$\" | awk '{print $9}'"
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        app_name = line.strip()
                        if app_name:
                            applications.append({
                                "name": app_name.replace(".app", ""),
                                "version": ""
                            })
            
            elif self.os_type == "Linux":
                # On Linux, list desktop entries
                command = "find /usr/share/applications -name \"*.desktop\" -exec basename {} \\; | sort"
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        app_name = line.strip().replace(".desktop", "")
                        if app_name:
                            applications.append({
                                "name": app_name,
                                "version": ""
                            })
            
            return {
                "success": True,
                "applications": applications,
                "count": len(applications)
            }
        
        except Exception as e:
            logger.error(f"Error listing applications: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e), "applications": [], "count": 0}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            logger.info("Getting system information")
            
            # Get CPU information
            cpu_count = psutil.cpu_count(logical=True)
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Get memory information
            memory = psutil.virtual_memory()
            memory_total = memory.total
            memory_available = memory.available
            memory_used = memory.used
            memory_percent = memory.percent
            
            # Get disk information
            disk = psutil.disk_usage('/')
            disk_total = disk.total
            disk_used = disk.used
            disk_free = disk.free
            disk_percent = disk.percent
            
            # Get platform information
            system = platform.system()
            release = platform.release()
            version = platform.version()
            machine = platform.machine()
            processor = platform.processor()
            
            return {
                "success": True,
                "cpu": {
                    "count": cpu_count,
                    "usage_percent": cpu_usage
                },
                "memory": {
                    "total": memory_total,
                    "available": memory_available,
                    "used": memory_used,
                    "percent": memory_percent
                },
                "disk": {
                    "total": disk_total,
                    "used": disk_used,
                    "free": disk_free,
                    "percent": disk_percent
                },
                "platform": {
                    "system": system,
                    "release": release,
                    "version": version,
                    "machine": machine,
                    "processor": processor
                }
            }
        
        except Exception as e:
            logger.error(f"Error getting system information: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def get_running_processes(self) -> Dict[str, Any]:
        """Get list of running processes"""
        try:
            logger.info("Getting running processes")
            
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
                try:
                    proc_info = proc.info
                    processes.append({
                        "pid": proc_info['pid'],
                        "name": proc_info['name'],
                        "username": proc_info['username'],
                        "memory_percent": proc_info['memory_percent'],
                        "cpu_percent": proc_info['cpu_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort processes by memory usage (descending)
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            return {
                "success": True,
                "processes": processes,
                "count": len(processes)
            }
        
        except Exception as e:
            logger.error(f"Error getting running processes: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e), "processes": [], "count": 0}
