#!/usr/bin/env python3
"""
Claude Code Integration MCP Server - Test Suite
Comprehensive testing for enhanced Claude Code integration
"""

import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_server import (
    EnhancedClaudeCodeMCP, 
    TaskStatus, 
    TaskPriority, 
    ProjectContext, 
    TaskContext
)

class TestEnhancedClaudeCodeMCP(unittest.TestCase):
    """Test suite for Enhanced Claude Code MCP Server"""
    
    def setUp(self):
        """Set up test environment"""
        self.mcp = EnhancedClaudeCodeMCP()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_project_type_detection(self):
        """Test automatic project type detection"""
        # Create test files
        test_cases = [
            ("package.json", "nodejs"),
            ("requirements.txt", "python"),
            ("pyproject.toml", "python"),
            ("Cargo.toml", "rust"),
            ("pom.xml", "java"),
            ("go.mod", "go"),
            ("composer.json", "php")
        ]
        
        for filename, expected_type in test_cases:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create test file
                test_file = Path(temp_dir) / filename
                test_file.touch()
                
                # Test detection
                detected_type = self.mcp._detect_project_type(temp_dir)
                self.assertEqual(detected_type, expected_type, 
                               f"Failed to detect {expected_type} for {filename}")
    
    def test_task_priority_ordering(self):
        """Test task priority system"""
        task_ids = []
        priorities = [TaskPriority.LOW, TaskPriority.CRITICAL, TaskPriority.NORMAL, TaskPriority.HIGH]
        
        # Create tasks with different priorities
        for i, priority in enumerate(priorities):
            task_id = f"task_{i}"
            task = TaskContext(
                task_id=task_id,
                description=f"Test task {i}",
                project_context=None,
                priority=priority,
                created_at=datetime.now()
            )
            self.mcp.tasks[task_id] = task
            self.mcp.task_queue.append(task_id)
            task_ids.append(task_id)
        
        # Test prioritization
        prioritized = self.mcp._prioritize_tasks()
        
        # Should be ordered: CRITICAL, HIGH, NORMAL, LOW
        expected_order = ["task_1", "task_3", "task_2", "task_0"]
        self.assertEqual(prioritized, expected_order)
    
    @patch('subprocess.run')
    def test_claude_code_availability_check(self, mock_run):
        """Test Claude Code CLI availability checking"""
        # Test successful check
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "claude-code v1.0.0"
        
        result = self.mcp._check_claude_code_availability()
        self.assertTrue(result)
        
        # Test failed check
        mock_run.side_effect = FileNotFoundError()
        result = self.mcp._check_claude_code_availability()
        self.assertFalse(result)
    
    def test_project_context_creation(self):
        """Test project context analysis and creation"""
        # Create a mock Node.js project
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create package.json
            package_json = {
                "name": "test-project",
                "version": "1.0.0",
                "dependencies": {
                    "express": "^4.18.0",
                    "lodash": "^4.17.21"
                }
            }
            
            package_path = Path(temp_dir) / "package.json"
            with open(package_path, 'w') as f:
                json.dump(package_json, f)
            
            # Test analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                project_context = loop.run_until_complete(
                    self.mcp._analyze_project(temp_dir)
                )
            finally:
                loop.close()
            
            # Verify results
            self.assertEqual(project_context.type, "nodejs")
            self.assertEqual(project_context.build_command, "npm run build")
            self.assertEqual(project_context.test_command, "npm test")
            self.assertIn("express", project_context.dependencies)
            self.assertIn("lodash", project_context.dependencies)
    
    def test_command_building(self):
        """Test Claude Code command construction"""
        project_context = ProjectContext(
            path="/test/project",
            name="test-project",
            type="python"
        )
        
        task = TaskContext(
            task_id="test-task",
            description="Implement feature X",
            project_context=project_context,
            priority=TaskPriority.NORMAL,
            created_at=datetime.now()
        )
        
        cmd = self.mcp._build_claude_code_command(task)
        
        expected = [
            "claude-code",
            "--project", "/test/project",
            "--task", "Implement feature X",
            "--project-type", "python"
        ]
        
        self.assertEqual(cmd, expected)
    
    def test_task_lifecycle(self):
        """Test complete task lifecycle"""
        # Create project context
        project_context = ProjectContext(
            path=self.test_dir,
            name="test-project",
            type="python"
        )
        
        self.mcp.projects[self.test_dir] = project_context
        self.mcp.active_project_path = self.test_dir
        
        # Create task
        task_id = "test-task-123"
        task = TaskContext(
            task_id=task_id,
            description="Test task execution",
            project_context=project_context,
            priority=TaskPriority.NORMAL,
            created_at=datetime.now()
        )
        
        self.mcp.tasks[task_id] = task
        
        # Test status progression
        self.assertEqual(task.status, TaskStatus.QUEUED)
        
        task.status = TaskStatus.STARTED
        self.assertEqual(task.status, TaskStatus.STARTED)
        
        task.status = TaskStatus.RUNNING
        self.assertEqual(task.status, TaskStatus.RUNNING)
        
        task.status = TaskStatus.COMPLETED
        task.exit_code = 0
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.exit_code, 0)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for real-world usage"""
    
    def setUp(self):
        self.mcp = EnhancedClaudeCodeMCP()
    
    def test_multi_project_management(self):
        """Test managing multiple projects simultaneously"""
        projects = [
            ("/path/to/frontend", "nodejs"),
            ("/path/to/backend", "python"),
            ("/path/to/mobile", "react-native")
        ]
        
        for path, project_type in projects:
            project_context = ProjectContext(
                path=path,
                name=Path(path).name,
                type=project_type
            )
            self.mcp.projects[path] = project_context
        
        # Verify all projects are tracked
        self.assertEqual(len(self.mcp.projects), 3)
        self.assertIn("/path/to/frontend", self.mcp.projects)
        self.assertIn("/path/to/backend", self.mcp.projects)
        self.assertIn("/path/to/mobile", self.mcp.projects)
    
    def test_task_dependency_management(self):
        """Test task dependency handling"""
        # Create dependent tasks
        task1_id = "build-backend"
        task2_id = "deploy-frontend" 
        task3_id = "run-integration-tests"
        
        tasks = [
            TaskContext(
                task_id=task1_id,
                description="Build backend services",
                project_context=None,
                priority=TaskPriority.HIGH,
                created_at=datetime.now()
            ),
            TaskContext(
                task_id=task2_id,
                description="Deploy frontend application",
                project_context=None,
                priority=TaskPriority.NORMAL,
                created_at=datetime.now(),
                dependencies=[task1_id]
            ),
            TaskContext(
                task_id=task3_id,
                description="Run integration test suite",
                project_context=None,
                priority=TaskPriority.CRITICAL,
                created_at=datetime.now(),
                dependencies=[task1_id, task2_id]
            )
        ]
        
        for task in tasks:
            self.mcp.tasks[task.task_id] = task
            self.mcp.task_queue.append(task.task_id)
        
        # Verify dependency tracking
        self.assertEqual(len(self.mcp.tasks[task2_id].dependencies), 1)
        self.assertEqual(len(self.mcp.tasks[task3_id].dependencies), 2)
        self.assertIn(task1_id, self.mcp.tasks[task2_id].dependencies)
        self.assertIn(task1_id, self.mcp.tasks[task3_id].dependencies)
        self.assertIn(task2_id, self.mcp.tasks[task3_id].dependencies)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and recovery mechanisms"""
    
    def setUp(self):
        self.mcp = EnhancedClaudeCodeMCP()
    
    def test_invalid_project_path(self):
        """Test handling of invalid project paths"""
        invalid_path = "/nonexistent/path/to/project"
        
        # Should handle gracefully without crashing
        try:
            project_type = self.mcp._detect_project_type(invalid_path)
            # Should return None for nonexistent paths
            self.assertIsNone(project_type)
        except Exception as e:
            self.fail(f"Should handle invalid paths gracefully, but raised: {e}")
    
    def test_git_error_handling(self):
        """Test git operation error handling"""
        # Test with directory that's not a git repository
        with tempfile.TemporaryDirectory() as temp_dir:
            remote, branch = self.mcp._get_git_info(temp_dir)
            # Should return None, None for non-git directories
            self.assertIsNone(remote)
            self.assertIsNone(branch)
    
    def test_task_not_found_error(self):
        """Test handling of invalid task IDs"""
        invalid_task_id = "nonexistent-task-123"
        
        # Should return appropriate error response
        result = monitor_task_progress(invalid_task_id)
        self.assertFalse(result["success"])
        self.assertIn("not found", result["message"])


if __name__ == "__main__":
    # Import datetime for tests
    from datetime import datetime
    
    # Import the tool functions for testing
    from enhanced_server import (
        check_claude_code_availability,
        analyze_project,
        set_active_project,
        delegate_coding_task,
        monitor_task_progress,
        get_task_results,
        list_active_tasks,
        get_system_status
    )
    
    # Run the test suite
    unittest.main(verbosity=2)
