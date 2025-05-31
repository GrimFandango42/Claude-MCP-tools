#!/usr/bin/env python3
"""
Environment Detection Utility for Claude MCP Tools
Automatically detects system capabilities and recommends optimal tool strategies
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

class EnvironmentDetector:
    """Smart environment detection for optimal MCP tool selection"""
    
    def __init__(self):
        self.system = platform.system()
        self.architecture = platform.architecture()[0]
        self.python_path = sys.executable
        self.is_wsl = self._detect_wsl()
        self.is_docker = self._detect_docker()
        self.package_managers = self._detect_package_managers()
        
    def _detect_wsl(self) -> bool:
        """Detect Windows Subsystem for Linux"""
        try:
            with open('/proc/version', 'r') as f:
                content = f.read().lower()
                return 'microsoft' in content or 'wsl' in content
        except:
            return False
    
    def _detect_docker(self) -> bool:
        """Detect Docker container environment"""
        return os.path.exists('/.dockerenv') or os.path.exists('/proc/1/cgroup')
    
    def _detect_package_managers(self) -> dict:
        """Detect available package managers"""
        managers = {}
        
        # Python package managers
        for manager in ['pip', 'pip3', 'conda', 'poetry', 'pipx']:
            managers[manager] = self._command_exists(manager)
        
        # System package managers
        if self.system == 'Linux':
            for manager in ['apt', 'yum', 'dnf', 'pacman']:
                managers[manager] = self._command_exists(manager)
        elif self.system == 'Darwin':
            managers['brew'] = self._command_exists('brew')
        elif self.system == 'Windows':
            managers['choco'] = self._command_exists('choco')
            managers['winget'] = self._command_exists('winget')
        
        return managers
    
    def _command_exists(self, command: str) -> bool:
        """Check if command exists in PATH"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, check=False, timeout=5)
            return True
        except:
            return False
    
    def get_python_strategy(self) -> dict:
        """Get optimal Python installation strategy"""
        strategy = {
            'primary_python': self.python_path,
            'package_manager': 'pip',
            'install_method': 'direct',
            'virtual_env_needed': False,
            'sudo_required': False
        }
        
        # WSL detected - prefer Windows Python for MCP compatibility
        if self.is_wsl:
            windows_python_paths = [
                'C:\\\\Users\\\\Nithin\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python312\\\\python.exe',
                'C:\\\\Python312\\\\python.exe',
                'C:\\\\Program Files\\\\Python312\\\\python.exe'
            ]
            
            for path in windows_python_paths:
                wsl_path = f'/mnt/c/{path[3:].replace("\\\\\\\\", "/")}'
                if Path(wsl_path).exists():
                    strategy.update({
                        'primary_python': path,
                        'install_method': 'windows_native',
                        'recommendation': 'Use Windows Python for MCP server compatibility'
                    })
                    break
        
        # Check for externally managed environment
        if self.system == 'Linux' and not self.is_wsl:
            try:
                result = subprocess.run([self.python_path, '-m', 'pip', 'install', '--help'], 
                                      capture_output=True, text=True, timeout=5)
                if 'externally-managed-environment' in result.stderr:
                    strategy.update({
                        'virtual_env_needed': True,
                        'install_method': 'venv_or_pipx',
                        'recommendation': 'Use virtual environment or pipx'
                    })
            except:
                pass
        
        return strategy
    
    def get_tool_recommendations(self) -> dict:
        """Get tool usage recommendations based on environment"""
        recommendations = {
            'file_operations': 'filesystem_mcp',  # Always optimal
            'code_editing': 'text_editor_20250429',  # Always optimal
            'system_commands': 'bash_20250124',
            'package_installation': 'bash_20250124',
            'gui_automation': 'computer_20250124'
        }
        
        # Adjust for WSL
        if self.is_wsl:
            recommendations.update({
                'package_installation': 'windows_native_script',
                'system_commands': 'hybrid_wsl_windows',
                'note': 'WSL detected - prefer Windows-native tools for MCP compatibility'
            })
        
        # Adjust for Docker
        if self.is_docker:
            recommendations.update({
                'package_installation': 'dockerfile_approach',
                'note': 'Docker detected - consider containerized solutions'
            })
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate comprehensive environment report"""
        strategy = self.get_python_strategy()
        tools = self.get_tool_recommendations()
        
        report = f"""
# 🔍 ENVIRONMENT ANALYSIS REPORT

## System Information
- **OS**: {self.system} ({self.architecture})
- **Python**: {self.python_path}
- **WSL**: {'✅ Detected' if self.is_wsl else '❌ Not detected'}
- **Docker**: {'✅ Detected' if self.is_docker else '❌ Not detected'}

## Package Managers Available
{chr(10).join([f"- **{name}**: {'✅ Available' if available else '❌ Not found'}" 
               for name, available in self.package_managers.items()])}

## Recommended Tool Strategy
{chr(10).join([f"- **{task}**: {tool}" for task, tool in tools.items() if task != 'note'])}

## Python Installation Strategy
- **Method**: {strategy['install_method']}
- **Primary Python**: {strategy['primary_python']}
- **Virtual Env Needed**: {'✅ Yes' if strategy.get('virtual_env_needed') else '❌ No'}
- **Recommendation**: {strategy.get('recommendation', 'Standard pip installation')}

## Efficiency Recommendations
1. **File Operations**: Always use filesystem MCP (30x faster than GUI)
2. **Code Editing**: Always use text_editor_20250429 (25x faster than GUI)
3. **Package Installation**: {tools.get('package_installation', 'bash_20250124')}
4. **System Commands**: {tools.get('system_commands', 'bash_20250124')}

{f"⚠️ **Note**: {tools.get('note', '')}" if tools.get('note') else ""}
"""
        return report

def quick_environment_check() -> dict:
    """Quick environment check for immediate tool selection"""
    detector = EnvironmentDetector()
    return {
        'is_wsl': detector.is_wsl,
        'system': detector.system,
        'python_strategy': detector.get_python_strategy(),
        'tool_recommendations': detector.get_tool_recommendations()
    }

if __name__ == "__main__":
    detector = EnvironmentDetector()
    print(detector.generate_report())