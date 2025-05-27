#!/usr/bin/env python3
"""
Claude Code Integration MCP - Usage Examples
Demonstrates advanced usage patterns and integration scenarios
"""

import json
import time
from pathlib import Path

# Example usage scenarios for the Enhanced Claude Code Integration MCP

def example_single_project_workflow():
    """Example: Complete workflow for a single project"""
    print("🚀 Single Project Workflow Example")
    print("="*50)
    
    # Step 1: Check Claude Code availability
    availability = check_claude_code_availability()
    print(f"Claude Code Available: {availability['available']}")
    
    if not availability['available']:
        print("❌ Claude Code CLI not available. Please install it first.")
        return
    
    # Step 2: Analyze and set active project
    project_path = "/path/to/my-awesome-app"
    
    print(f"\n📁 Analyzing project: {project_path}")
    analysis = analyze_project(project_path)
    
    if analysis['success']:
        print(f"✅ Project analyzed: {analysis['project_context']['name']}")
        print(f"   Type: {analysis['project_context']['type']}")
        print(f"   Dependencies: {len(analysis['project_context']['dependencies'])}")
        
        # Set as active project
        set_result = set_active_project(project_path)
        print(f"✅ Active project set: {set_result['success']}")
    
    # Step 3: Delegate coding tasks with different priorities
    tasks = [
        {
            "description": "Fix critical security vulnerability in authentication",
            "priority": "critical",
            "tags": ["security", "urgent"]
        },
        {
            "description": "Implement new user dashboard with analytics",
            "priority": "high", 
            "tags": ["feature", "ui"]
        },
        {
            "description": "Add comprehensive unit tests for user service", 
            "priority": "normal",
            "tags": ["testing", "quality"]
        },
        {
            "description": "Update documentation for API endpoints",
            "priority": "low",
            "tags": ["docs", "maintenance"]
        }
    ]
    
    task_ids = []
    print(f"\n🎯 Delegating {len(tasks)} tasks:")
    
    for i, task_info in enumerate(tasks):
        result = delegate_coding_task(
            task_description=task_info["description"],
            priority=task_info["priority"],
            tags=task_info["tags"]
        )
        
        if result['success']:
            task_ids.append(result['task_id'])
            print(f"   {i+1}. ✅ {task_info['priority'].upper()}: {task_info['description'][:50]}...")
            print(f"      Task ID: {result['task_id']}")
        else:
            print(f"   {i+1}. ❌ Failed: {result['message']}")
    
    # Step 4: Monitor task progress
    print(f"\n📊 Monitoring {len(task_ids)} tasks:")
    
    for task_id in task_ids:
        progress = monitor_task_progress(task_id)
        if progress['success']:
            print(f"   📋 {task_id[:8]}... | Status: {progress['status']} | Priority: {progress['priority']}")
            if progress.get('execution_time_seconds'):
                print(f"      ⏱️  Execution time: {progress['execution_time_seconds']:.2f}s")
        else:
            print(f"   ❌ {task_id[:8]}... | Error: {progress['message']}")
    
    # Step 5: Get system overview
    print(f"\n🖥️  System Status:")
    status = get_system_status()
    if status['success']:
        stats = status['task_statistics']
        print(f"   📈 Tasks: {stats['total']} total, {stats['running']} running, {stats['completed']} completed")
        print(f"   💾 Projects: {status['project_statistics']['total']} analyzed")
        if 'system_resources' in status and 'cpu_percent' in status['system_resources']:
            resources = status['system_resources']
            print(f"   🖥️  Resources: {resources['cpu_percent']:.1f}% CPU, {resources['memory_percent']:.1f}% Memory")


def example_multi_project_coordination():
    """Example: Coordinating tasks across multiple projects"""
    print("\n🏗️  Multi-Project Coordination Example")
    print("="*50)
    
    # Define multiple related projects
    projects = [
        {"path": "/path/to/ecommerce-frontend", "role": "React frontend"},
        {"path": "/path/to/ecommerce-backend", "role": "Python API server"},
        {"path": "/path/to/ecommerce-mobile", "role": "React Native mobile app"},
        {"path": "/path/to/shared-components", "role": "Shared UI library"}
    ]
    
    # Analyze all projects
    print("📁 Analyzing multiple projects:")
    for project in projects:
        analysis = analyze_project(project["path"])
        if analysis['success']:
            project_name = analysis['project_context']['name']
            project_type = analysis['project_context']['type']
            print(f"   ✅ {project_name} ({project_type}) - {project['role']}")
        else:
            print(f"   ❌ Failed to analyze {project['path']}")
    
    # Coordinate related tasks across projects
    coordinated_tasks = [
        {
            "description": "Update shared API types and interfaces",
            "project": "/path/to/shared-components",
            "priority": "high",
            "tags": ["api", "types", "shared"]
        },
        {
            "description": "Implement new product search API endpoints", 
            "project": "/path/to/ecommerce-backend",
            "priority": "high",
            "tags": ["api", "backend", "search"],
            "dependencies": []  # Will be populated with shared components task
        },
        {
            "description": "Update frontend to use new search API",
            "project": "/path/to/ecommerce-frontend", 
            "priority": "normal",
            "tags": ["frontend", "search", "integration"]
        },
        {
            "description": "Add search functionality to mobile app",
            "project": "/path/to/ecommerce-mobile",
            "priority": "normal", 
            "tags": ["mobile", "search", "feature"]
        }
    ]
    
    task_chain = []
    print(f"\n🔗 Creating coordinated task chain:")
    
    for i, task_info in enumerate(coordinated_tasks):
        # Add dependencies to later tasks
        dependencies = task_chain[-1:] if i > 0 else []
        
        result = delegate_coding_task(
            task_description=task_info["description"],
            project_path=task_info["project"],
            priority=task_info["priority"],
            tags=task_info["tags"],
            dependencies=dependencies
        )
        
        if result['success']:
            task_chain.append(result['task_id'])
            project_name = Path(task_info["project"]).name
            print(f"   {i+1}. ✅ {project_name}: {task_info['description'][:40]}...")
            if dependencies:
                print(f"      🔗 Depends on: {len(dependencies)} previous task(s)")
        else:
            print(f"   {i+1}. ❌ Failed: {result['message']}")
    
    print(f"\n📊 Task chain created with {len(task_chain)} coordinated tasks")


def example_ci_cd_pipeline_integration():
    """Example: CI/CD pipeline task delegation"""
    print("\n🚀 CI/CD Pipeline Integration Example")
    print("="*50)
    
    project_path = "/path/to/production-app"
    
    # Set active project
    set_active_project(project_path)
    
    # Define CI/CD pipeline tasks
    pipeline_tasks = [
        {
            "description": "Run comprehensive test suite with coverage report",
            "priority": "critical", 
            "tags": ["testing", "ci", "quality-gate"],
            "phase": "Test"
        },
        {
            "description": "Build optimized production artifacts",
            "priority": "critical",
            "tags": ["build", "production", "artifacts"],
            "phase": "Build"
        },
        {
            "description": "Run security vulnerability scan",
            "priority": "high",
            "tags": ["security", "scanning", "compliance"],
            "phase": "Security"
        },
        {
            "description": "Deploy to staging environment with health checks",
            "priority": "high", 
            "tags": ["deployment", "staging", "validation"],
            "phase": "Deploy"
        },
        {
            "description": "Run automated integration tests against staging",
            "priority": "high",
            "tags": ["integration", "testing", "validation"],
            "phase": "Validation"
        },
        {
            "description": "Promote to production with blue-green deployment",
            "priority": "critical",
            "tags": ["production", "deployment", "blue-green"],
            "phase": "Production"
        }
    ]
    
    pipeline_task_ids = []
    print("🏭 Executing CI/CD pipeline:")
    
    for i, task_info in enumerate(pipeline_tasks):
        # Create dependencies on previous tasks for pipeline sequence
        dependencies = pipeline_task_ids[-1:] if i > 0 else []
        
        result = delegate_coding_task(
            task_description=task_info["description"],
            priority=task_info["priority"],
            tags=task_info["tags"],
            dependencies=dependencies
        )
        
        if result['success']:
            pipeline_task_ids.append(result['task_id'])
            print(f"   {i+1}. {task_info['phase']}: ✅ {task_info['description'][:50]}...")
            print(f"      🆔 Task ID: {result['task_id']}")
        else:
            print(f"   {i+1}. {task_info['phase']}: ❌ {result['message']}")
    
    # Monitor pipeline progress
    print(f"\n📈 Pipeline Progress Monitoring:")
    
    while True:
        all_tasks = list_active_tasks()
        if all_tasks['success']:
            active_count = all_tasks['total_active']
            completed_count = len([t for t in all_tasks.get('completed_tasks', [])])
            
            print(f"   📊 Active: {active_count}, Completed: {completed_count}")
            
            # Show detailed status for pipeline tasks
            for task_id in pipeline_task_ids:
                progress = monitor_task_progress(task_id)
                if progress['success']:
                    status = progress['status']
                    description = progress['description'][:30]
                    print(f"      • {task_id[:8]}... | {status.upper()} | {description}...")
            
            if active_count == 0:
                print("   ✅ Pipeline execution completed!")
                break
            
        time.sleep(5)  # Check every 5 seconds


def example_development_workflow():
    """Example: Typical development workflow with code quality gates"""
    print("\n💻 Development Workflow Example")
    print("="*50)
    
    project_path = "/path/to/feature-branch-project"
    
    # Development workflow tasks
    dev_tasks = [
        {
            "description": "Create feature branch for user authentication improvements",
            "priority": "normal",
            "tags": ["git", "branching", "setup"]
        },
        {
            "description": "Implement OAuth 2.0 integration with Google and GitHub",
            "priority": "high",
            "tags": ["feature", "auth", "oauth", "implementation"]
        },
        {
            "description": "Add comprehensive unit tests for authentication flows",
            "priority": "high", 
            "tags": ["testing", "unit-tests", "auth"]
        },
        {
            "description": "Run code linting and apply automatic fixes",
            "priority": "normal",
            "tags": ["quality", "linting", "style"]
        },
        {
            "description": "Perform static code analysis and security scan",
            "priority": "high",
            "tags": ["quality", "security", "analysis"]
        },
        {
            "description": "Update API documentation with new authentication endpoints",
            "priority": "normal",
            "tags": ["docs", "api", "documentation"]
        },
        {
            "description": "Create pull request with comprehensive description",
            "priority": "normal",
            "tags": ["git", "pr", "review"]
        }
    ]
    
    print("🛠️  Development Task Sequence:")
    
    dev_task_ids = []
    for i, task_info in enumerate(dev_tasks):
        result = delegate_coding_task(
            task_description=task_info["description"],
            project_path=project_path,
            priority=task_info["priority"],
            tags=task_info["tags"]
        )
        
        if result['success']:
            dev_task_ids.append(result['task_id'])
            print(f"   {i+1}. ✅ {task_info['description'][:60]}...")
        else:
            print(f"   {i+1}. ❌ {result['message']}")
    
    # Quality gate monitoring
    print(f"\n🚦 Quality Gate Monitoring:")
    
    quality_gates = ["testing", "quality", "security"]
    
    for gate in quality_gates:
        gate_tasks = [tid for tid in dev_task_ids 
                     if any(gate in tag for tag in 
                           next((t for t in dev_tasks 
                                if delegate_coding_task(t["description"], project_path, t["priority"], t["tags"])["task_id"] == tid), {}).get("tags", []))]
        
        print(f"   🔍 {gate.title()} Gate: Monitoring {len(gate_tasks)} tasks...")
        
        for task_id in gate_tasks:
            progress = monitor_task_progress(task_id)
            if progress['success']:
                status = progress['status']
                print(f"      • {status.upper()}: {progress['description'][:40]}...")


if __name__ == "__main__":
    """
    Run example scenarios to demonstrate Claude Code Integration MCP capabilities
    """
    
    print("🎯 Claude Code Integration MCP - Usage Examples")
    print("=" * 60)
    print("This script demonstrates advanced usage patterns for the Enhanced Claude Code Integration MCP Server")
    print()
    
    # Import the MCP tools (these would be available when running as an MCP server)
    try:
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
        
        # Run example scenarios
        example_single_project_workflow()
        example_multi_project_coordination() 
        example_ci_cd_pipeline_integration()
        example_development_workflow()
        
        print("\n🎉 All examples completed successfully!")
        print("\nThese examples demonstrate:")
        print("  • Single and multi-project management")
        print("  • Task prioritization and dependency handling")
        print("  • CI/CD pipeline integration")
        print("  • Development workflow automation")
        print("  • Quality gate monitoring")
        print("  • Real-time progress tracking")
        
    except ImportError as e:
        print(f"❌ Could not import MCP tools: {e}")
        print("This script should be run in the context of the MCP server environment.")
        print("To test the MCP server, use: python test_server.py")
