#!/usr/bin/env python3
"""
🚀 Claude Code Integration Test
Tests the working Claude Code installation with asyncio event loop fix
"""

import subprocess
import asyncio
import sys
import os
from pathlib import Path
import shutil

class ClaudeCodeIntegration:
    def __init__(self):
        # Assume executables are in PATH
        self.node_executable = "node"
        self.npm_executable = "npm"
        self.claude_executable = "claude"
        self.test_project_base_dir = Path(".").resolve() # Base for test project
        
    async def run_subprocess_async(self, cmd, cwd=None, timeout=30):
        """Run subprocess command asynchronously to avoid event loop conflicts"""
        try:
            # Use asyncio.create_subprocess_shell instead of subprocess.run
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            return {
                'returncode': process.returncode,
                'stdout': stdout.decode() if stdout else '',
                'stderr': stderr.decode() if stderr else '',
                'success': process.returncode == 0
            }
        except asyncio.TimeoutError:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out',
                'success': False
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def run_sync_subprocess(self, cmd, cwd=None, timeout=30):
        """Run subprocess synchronously (fallback method)"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=os.environ.copy()
            )
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out',
                'success': False
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    async def test_claude_installation(self):
        """Test Claude Code installation"""
        print("🔍 Testing Claude Code Installation...")
        
        # Test Node.js version
        node_result = await self.run_subprocess_async(f"{self.node_executable} --version")
        if node_result['success']:
            print(f"   ✅ Node.js: {node_result['stdout'].strip()}")
        else:
            print(f"   ❌ Node.js test failed: {node_result['stderr']}")
            return False
        
        # Test npm version
        npm_result = await self.run_subprocess_async(f"{self.npm_executable} --version")
        if npm_result['success']:
            print(f"   ✅ NPM: {npm_result['stdout'].strip()}")
        else:
            print(f"   ❌ NPM test failed: {npm_result['stderr']}")
            return False
        
        # Test Claude Code version
        claude_result = await self.run_subprocess_async(f"{self.claude_executable} --version")
        if claude_result['success']:
            print(f"   ✅ Claude Code: {claude_result['stdout'].strip()}")
        else:
            print(f"   ❌ Claude Code test failed: {claude_result['stderr']}")
            return False
        
        print("   🎯 All installation tests passed!")
        return True
    
    async def test_claude_help(self):
        """Test Claude Code help command"""
        print("\n📚 Testing Claude Code Help Command...")
        
        help_result = await self.run_subprocess_async(f"{self.claude_executable} --help")
        if help_result['success'] and 'Usage: claude' in help_result['stdout']:
            print("   ✅ Help command works correctly")
            print("   📋 Available commands detected:")
            help_lines = help_result['stdout'].split('\n')
            for line in help_lines:
                if 'Commands:' in line:
                    idx = help_lines.index(line)
                    for cmd_line in help_lines[idx+1:idx+6]:
                        if cmd_line.strip() and not cmd_line.startswith(' '):
                            break
                        if cmd_line.strip():
                            print(f"      • {cmd_line.strip()}")
            return True
        else:
            print(f"   ❌ Help command failed: {help_result['stderr']}")
            return False
    
    async def test_project_setup(self):
        """Test setting up a project directory"""
        print("\n📁 Testing Project Setup...")
        
        test_dir = self.test_project_base_dir / "claude_integration_test_project"
        
        # Clean up existing test directory if it exists
        if test_dir.exists():
            shutil.rmtree(test_dir)

        # Create test directory
        setup_cmd = f"""
        mkdir -p {test_dir} && \
        cd {test_dir} && \
        echo '# Claude Code Integration Test' > README.md && \
        echo 'console.log("Hello from Claude Code!");' > hello.js && \
        echo 'def greet(name): return f"Hello {{name}} from Claude Code!"' > hello.py && \
        ls -la
        """
        
        setup_result = await self.run_subprocess_async(setup_cmd)
        if setup_result['success']:
            print("   ✅ Test project created successfully")
            print("   📂 Project contents:")
            for line in setup_result['stdout'].split('\n'):
                if line.strip() and ('README.md' in line or 'hello.' in line):
                    print(f"      • {line.strip()}")
            return test_dir
        else:
            print(f"   ❌ Project setup failed: {setup_result['stderr']}")
            return None
    
    async def test_claude_print_mode(self, project_dir):
        """Test Claude Code in print mode (non-interactive)"""
        print("\n🖨️  Testing Claude Code Print Mode...")
        
        # Test with a simple programming question
        test_prompt = "Explain what this JavaScript code does: console.log('Hello from Claude Code!');"
        
        claude_cmd = f'cd {project_dir} && {self.claude_executable} --print "{test_prompt}"'
        
        claude_result = await self.run_subprocess_async(claude_cmd, timeout=60)
        
        if claude_result['success'] and claude_result['stdout'].strip():
            print("   ✅ Claude Code print mode works!")
            response = claude_result['stdout'].strip()[:200]
            print(f"   💬 Response preview: {response}...")
            return True
        else:
            print(f"   ❌ Claude Code print mode failed")
            if claude_result['stderr']:
                print(f"   🔍 Error details: {claude_result['stderr'][:200]}...")
            if "authentication" in claude_result['stderr'].lower():
                print("   ℹ️  This is expected on first run - Claude Code needs authentication")
                print("   🔑 Run 'claude config' to set up authentication")
                return "auth_needed"
            return False
    
    async def run_integration_test(self):
        """Run complete integration test suite"""
        print("🚀 CLAUDE CODE INTEGRATION TEST SUITE")
        print("="*60)
        
        try:
            if not await self.test_claude_installation():
                return

            if not await self.test_claude_help():
                return

            project_dir = await self.test_project_setup()
            if not project_dir:
                return

            print_mode_result = await self.test_claude_print_mode(project_dir)
            
            # Clean up test project directory
            if Path(project_dir).exists():
                print(f"\n🧹 Cleaning up test project directory: {project_dir}")
                shutil.rmtree(project_dir)
                print("   ✅ Cleanup successful.")

            if print_mode_result == "auth_needed":
                print("\n🔶 TEST SUITE COMPLETED WITH AUTHENTICATION REQUIRED FOR CLAUDE CODE.")
            elif print_mode_result:
                print("\n✅ ALL CLAUDE CODE INTEGRATION TESTS PASSED SUCCESSFULLY!")
            else:
                print("\n❌ SOME CLAUDE CODE INTEGRATION TESTS FAILED.")
                
        except Exception as e:
            print(f"\n💥 An error occurred during the integration test: {e}")
        finally:
            print("="*60)
            print("🏁 Test suite finished.")

async def main():
    """Main test runner"""
    integration = ClaudeCodeIntegration()
    await integration.run_integration_test()

if __name__ == "__main__":
    # Handle the asyncio event loop issue by using the current running loop
    try:
        # Try to get the current running loop
        loop = asyncio.get_running_loop()
        # If we're already in a loop, schedule the coroutine
        task = loop.create_task(main())
        # Note: In a real scenario, you'd need to handle this differently
        # For now, we'll just create the task
        print("⚠️  Running in existing event loop - creating task")
    except RuntimeError:
        # No loop is running, safe to use asyncio.run()
        asyncio.run(main())
