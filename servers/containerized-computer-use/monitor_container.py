#!/usr/bin/env python3
"""
Real-time monitoring dashboard for containerized Computer Use server
Displays container health, resource usage, and MCP activity
"""

import subprocess
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple


class ContainerMonitor:
    """Monitor containerized Computer Use server."""
    
    def __init__(self):
        self.container_name = "windows-computer-use"
        self.refresh_interval = 2  # seconds
        self.log_lines = 10
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_container_stats(self) -> Dict[str, any]:
        """Get container resource statistics."""
        cmd = ["docker", "stats", self.container_name, "--no-stream", "--format", "json"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
        except:
            pass
        return {}
    
    def get_container_info(self) -> Dict[str, any]:
        """Get container information."""
        cmd = ["docker", "inspect", self.container_name]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data:
                    return data[0]
        except:
            pass
        return {}
    
    def get_container_processes(self) -> List[str]:
        """Get running processes in container."""
        cmd = ["docker", "top", self.container_name]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                return lines[:10]  # First 10 processes
        except:
            pass
        return []
    
    def get_container_logs(self) -> List[str]:
        """Get recent container logs."""
        cmd = ["docker", "logs", self.container_name, "--tail", str(self.log_lines)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stderr.strip().split('\n')[-self.log_lines:]
        except:
            pass
        return []
    
    def get_port_status(self) -> Dict[str, bool]:
        """Check if ports are accessible."""
        ports = {
            "5900": "VNC Server",
            "8080": "MCP Server"
        }
        
        status = {}
        for port, service in ports.items():
            # Simple check if port is mapped
            cmd = ["docker", "port", self.container_name, port]
            result = subprocess.run(cmd, capture_output=True, text=True)
            status[service] = result.returncode == 0 and bool(result.stdout)
        
        return status
    
    def get_filesystem_usage(self) -> Dict[str, str]:
        """Get filesystem usage in container."""
        cmd = ["docker", "exec", self.container_name, "df", "-h", "/"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        return {
                            "size": parts[1],
                            "used": parts[2],
                            "available": parts[3],
                            "percent": parts[4]
                        }
        except:
            pass
        return {}
    
    def format_bytes(self, bytes_str: str) -> str:
        """Format byte string for display."""
        # Remove 'iB' suffix if present
        if bytes_str.endswith('iB'):
            return bytes_str[:-2] + 'B'
        return bytes_str
    
    def display_dashboard(self):
        """Display the monitoring dashboard."""
        self.clear_screen()
        
        # Header
        print("="*80)
        print(f"{'Containerized Computer Use Monitor':^80}")
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^80}")
        print("="*80)
        
        # Container Info
        info = self.get_container_info()
        if info:
            state = info.get('State', {})
            print(f"\n{'Container Status:':<20} {'RUNNING' if state.get('Running') else 'STOPPED'}")
            print(f"{'Container ID:':<20} {info.get('Id', '')[:12]}")
            print(f"{'Created:':<20} {info.get('Created', '')[:19]}")
            print(f"{'Restart Count:':<20} {info.get('RestartCount', 0)}")
        
        # Resource Usage
        stats = self.get_container_stats()
        if stats:
            print(f"\n{'='*40} Resource Usage {'='*40}")
            print(f"{'CPU Usage:':<20} {stats.get('CPUPerc', 'N/A')}")
            print(f"{'Memory Usage:':<20} {stats.get('MemUsage', 'N/A')} ({stats.get('MemPerc', 'N/A')})")
            print(f"{'Network I/O:':<20} {stats.get('NetIO', 'N/A')}")
            print(f"{'Block I/O:':<20} {stats.get('BlockIO', 'N/A')}")
        
        # Filesystem Usage
        fs_usage = self.get_filesystem_usage()
        if fs_usage:
            print(f"\n{'='*40} Filesystem Usage {'='*40}")
            print(f"{'Total Size:':<20} {fs_usage.get('size', 'N/A')}")
            print(f"{'Used:':<20} {fs_usage.get('used', 'N/A')} ({fs_usage.get('percent', 'N/A')})")
            print(f"{'Available:':<20} {fs_usage.get('available', 'N/A')}")
        
        # Port Status
        port_status = self.get_port_status()
        print(f"\n{'='*40} Service Status {'='*40}")
        for service, available in port_status.items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"{service:<20} {status}")
        
        # Running Processes
        processes = self.get_container_processes()
        if processes:
            print(f"\n{'='*40} Running Processes {'='*40}")
            for i, process in enumerate(processes[:5]):
                if i == 0:  # Header
                    print(f"{process}")
                    print("-"*80)
                else:
                    print(f"{process}")
        
        # Recent Logs
        logs = self.get_container_logs()
        if logs:
            print(f"\n{'='*40} Recent Logs {'='*40}")
            for log in logs[-5:]:
                if log.strip():
                    # Truncate long lines
                    display_log = log[:100] + "..." if len(log) > 100 else log
                    print(f"{display_log}")
        
        # Footer
        print("\n" + "="*80)
        print(f"{'Press Ctrl+C to exit | Refreshing every ' + str(self.refresh_interval) + 's':^80}")
    
    def run(self):
        """Run the monitoring dashboard."""
        print("Starting container monitor...")
        print(f"Monitoring container: {self.container_name}")
        
        # Check if container exists
        cmd = ["docker", "ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if self.container_name not in result.stdout:
            print(f"\nError: Container '{self.container_name}' does not exist!")
            print("Please create the container with: .\\setup.ps1")
            sys.exit(1)
        
        try:
            while True:
                self.display_dashboard()
                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
        except Exception as e:
            print(f"\n\nError: {e}")
            sys.exit(1)


def main():
    """Run the monitor."""
    monitor = ContainerMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
