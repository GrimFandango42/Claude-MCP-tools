#!/usr/bin/env python3
"""
Cleanup script to organize and archive redundant files in the Claude MCP Tools project.
This script safely moves redundant files to an archive structure while preserving important files.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
ARCHIVE_ROOT = PROJECT_ROOT / "archive" / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Files to archive from ClaudeDesktopAgent
CLAUDEDESKTOPAGENT_ARCHIVE = {
    "prototypes": [
        "basic_mcp_server.py",
        "simple_mcp_server.py", 
        "simple_mcp_server_8091.py",
        "cmd_mcp_server.py",
        "http_mcp_server.py",
        "ws_mcp_server.py",
        "mcp_screenshot.py",
        "simple_screenshot.py",
        "screenshot_server.py",
        "fixed_mcp_server.py",
    ],
    "test_files": [
        "test_client.py",
        "test_screenshot.py",
        "test_screenshot_tool.py",
        "diagnose_windows_server.py",
    ],
    "config_backups": [
        "claude_desktop_config_backup.json",
        "claude_mcp_config.json",
        "client_stdout.json",
    ],
    "batch_scripts": [
        "start_mcp_server.bat",
    ],
    "logs": [
        "*.log",
    ]
}

# Directories to remove entirely
REMOVE_DIRS = [
    "archive/legacy-firecrawl",
    "archive/legacy-servers",
]

# Files to keep (production files)
KEEP_FILES = {
    "ClaudeDesktopAgent": [
        "windows_fixed_mcp_server.py",
        "start_windows_fixed_server.bat",
        "test_windows_server.py",
        "README.md",
        "WINDOWS_FIXED_README.md",
        "requirements.txt",
        "claude_desktop_config.json",
        "app/",
        "tests/",
        "screenshots/",  # Keep screenshot directory
    ]
}

def create_archive_structure():
    """Create archive directory structure."""
    archive_dirs = [
        ARCHIVE_ROOT / "ClaudeDesktopAgent" / "prototypes",
        ARCHIVE_ROOT / "ClaudeDesktopAgent" / "test_files",
        ARCHIVE_ROOT / "ClaudeDesktopAgent" / "config_backups",
        ARCHIVE_ROOT / "ClaudeDesktopAgent" / "batch_scripts",
        ARCHIVE_ROOT / "ClaudeDesktopAgent" / "logs",
        ARCHIVE_ROOT / "removed_directories",
    ]
    
    for dir_path in archive_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return ARCHIVE_ROOT

def archive_claudedesktopagent_files():
    """Archive redundant files from ClaudeDesktopAgent."""
    agent_dir = PROJECT_ROOT / "ClaudeDesktopAgent"
    archived_files = []
    
    for category, files in CLAUDEDESKTOPAGENT_ARCHIVE.items():
        archive_category_dir = ARCHIVE_ROOT / "ClaudeDesktopAgent" / category
        
        for file_pattern in files:
            if "*" in file_pattern:
                # Handle glob patterns
                for file_path in agent_dir.glob(file_pattern):
                    if file_path.is_file():
                        dest = archive_category_dir / file_path.name
                        print(f"Archiving: {file_path.relative_to(PROJECT_ROOT)} -> {dest.relative_to(PROJECT_ROOT)}")
                        try:
                            shutil.move(str(file_path), str(dest))
                            archived_files.append(str(file_path.relative_to(PROJECT_ROOT)))
                        except PermissionError:
                            # If we can't move (e.g., file in use), copy instead
                            print(f"  Warning: Could not move {file_path.name} (in use), copying instead")
                            shutil.copy2(str(file_path), str(dest))
                            archived_files.append(str(file_path.relative_to(PROJECT_ROOT)) + " (copied)")
            else:
                # Handle specific files
                file_path = agent_dir / file_pattern
                if file_path.exists() and file_path.is_file():
                    dest = archive_category_dir / file_path.name
                    print(f"Archiving: {file_path.relative_to(PROJECT_ROOT)} -> {dest.relative_to(PROJECT_ROOT)}")
                    try:
                        shutil.move(str(file_path), str(dest))
                    except PermissionError:
                        # If we can't move (e.g., file in use), copy instead
                        print(f"  Warning: Could not move {file_path.name} (in use), copying instead")
                        shutil.copy2(str(file_path), str(dest))
                        # Note that we couldn't delete the original
                        archived_files.append(str(file_path.relative_to(PROJECT_ROOT)) + " (copied)")
                    else:
                        archived_files.append(str(file_path.relative_to(PROJECT_ROOT)))
    
    return archived_files

def remove_legacy_directories():
    """Remove legacy directories that are no longer needed."""
    removed_dirs = []
    
    for dir_path in REMOVE_DIRS:
        full_path = PROJECT_ROOT / dir_path
        if full_path.exists() and full_path.is_dir():
            dest = ARCHIVE_ROOT / "removed_directories" / Path(dir_path).name
            print(f"Removing directory: {dir_path} -> {dest.relative_to(PROJECT_ROOT)}")
            shutil.move(str(full_path), str(dest))
            removed_dirs.append(dir_path)
    
    return removed_dirs

def create_cleanup_report(archived_files, removed_dirs):
    """Create a detailed cleanup report."""
    report = {
        "cleanup_date": datetime.now().isoformat(),
        "archive_location": str(ARCHIVE_ROOT.relative_to(PROJECT_ROOT)),
        "archived_files": archived_files,
        "removed_directories": removed_dirs,
        "files_kept": {},
    }
    
    # Document kept files
    for location, keep_list in KEEP_FILES.items():
        kept = []
        location_path = PROJECT_ROOT / location
        for item in keep_list:
            item_path = location_path / item
            if item_path.exists():
                kept.append(item)
        report["files_kept"][location] = kept
    
    # Save report
    report_path = ARCHIVE_ROOT / "cleanup_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Also create a markdown report
    md_report_path = PROJECT_ROOT / "CLEANUP_REPORT.md"
    with open(md_report_path, 'w') as f:
        f.write(f"# Cleanup Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Archive Location\n`{report['archive_location']}`\n\n")
        
        f.write("## Archived Files\n")
        for file in archived_files:
            f.write(f"- `{file}`\n")
        
        f.write("\n## Removed Directories\n")
        for dir in removed_dirs:
            f.write(f"- `{dir}`\n")
        
        f.write("\n## Production Files Kept\n")
        for location, files in report["files_kept"].items():
            f.write(f"\n### {location}\n")
            for file in files:
                f.write(f"- `{file}`\n")
    
    return report_path, md_report_path

def main():
    """Main cleanup function."""
    print("Claude MCP Tools - Redundant Files Cleanup")
    print("==========================================\n")
    
    # Check for auto mode
    import sys
    auto_mode = len(sys.argv) > 1 and sys.argv[1] == '--auto'
    
    if not auto_mode:
        # Safety check
        response = input("This will move redundant files to archive. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cleanup cancelled.")
            return
    else:
        print("Running in auto mode...")
    
    print(f"\nCreating archive at: {ARCHIVE_ROOT.relative_to(PROJECT_ROOT)}")
    create_archive_structure()
    
    print("\nArchiving ClaudeDesktopAgent files...")
    archived_files = archive_claudedesktopagent_files()
    
    print("\nRemoving legacy directories...")
    removed_dirs = remove_legacy_directories()
    
    print("\nCreating cleanup report...")
    json_report, md_report = create_cleanup_report(archived_files, removed_dirs)
    
    print(f"\nCleanup complete!")
    print(f"- Archived {len(archived_files)} files")
    print(f"- Removed {len(removed_dirs)} directories")
    print(f"- JSON report: {json_report.relative_to(PROJECT_ROOT)}")
    print(f"- Markdown report: {md_report.relative_to(PROJECT_ROOT)}")
    
    print("\n✅ All redundant files have been safely archived.")
    print("You can find them in the archive directory if needed.")

if __name__ == "__main__":
    main()