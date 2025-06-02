#!/usr/bin/env python3
"""
Archive servers marked for removal in the consolidation plan.
Creates timestamped archive and moves servers safely.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
SERVERS_DIR = PROJECT_ROOT / "servers"
ARCHIVE_ROOT = PROJECT_ROOT / "archive" / f"server_consolidation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Servers to archive
SERVERS_TO_ARCHIVE = [
    "code-analysis-mcp",
    "code-quality-mcp", 
    "refactoring-mcp",
    "test-intelligence-mcp",
    "dependency-analysis-mcp",
    "code-intelligence-core",
    "knowledge-memory-mcp",
    # Note: claude-desktop-agent is in ClaudeDesktopAgent dir, not servers/
]

def create_archive_structure():
    """Create archive directory structure."""
    archive_dirs = [
        ARCHIVE_ROOT / "code-intelligence-stubs",
        ARCHIVE_ROOT / "memory-consolidation",
        ARCHIVE_ROOT / "desktop-consolidation",
    ]
    
    for dir_path in archive_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return ARCHIVE_ROOT

def archive_servers():
    """Archive the servers marked for removal."""
    archived = []
    errors = []
    
    for server_name in SERVERS_TO_ARCHIVE:
        server_path = SERVERS_DIR / server_name
        
        if not server_path.exists():
            print(f"Warning: Server directory not found: {server_name}")
            errors.append(f"{server_name}: Not found")
            continue
        
        # Determine archive category
        if "code-" in server_name:
            category = "code-intelligence-stubs"
        elif "memory" in server_name:
            category = "memory-consolidation"
        else:
            category = "other"
        
        dest_path = ARCHIVE_ROOT / category / server_name
        
        try:
            print(f"Archiving: {server_name} -> archive/{category}/")
            shutil.move(str(server_path), str(dest_path))
            archived.append({
                "server": server_name,
                "from": str(server_path.relative_to(PROJECT_ROOT)),
                "to": str(dest_path.relative_to(PROJECT_ROOT))
            })
        except Exception as e:
            print(f"Error archiving {server_name}: {e}")
            errors.append(f"{server_name}: {str(e)}")
    
    # Archive claude-desktop-agent separately
    agent_path = PROJECT_ROOT / "ClaudeDesktopAgent"
    if agent_path.exists():
        print(f"Archiving: ClaudeDesktopAgent -> archive/desktop-consolidation/")
        dest_path = ARCHIVE_ROOT / "desktop-consolidation" / "ClaudeDesktopAgent"
        try:
            shutil.copytree(str(agent_path), str(dest_path))
            archived.append({
                "server": "ClaudeDesktopAgent",
                "from": "ClaudeDesktopAgent/",
                "to": str(dest_path.relative_to(PROJECT_ROOT)),
                "note": "Copied instead of moved - may need manual cleanup"
            })
        except Exception as e:
            print(f"Error archiving ClaudeDesktopAgent: {e}")
            errors.append(f"ClaudeDesktopAgent: {str(e)}")
    
    return archived, errors

def create_archive_report(archived, errors):
    """Create a report of the archival process."""
    report = {
        "archive_date": datetime.now().isoformat(),
        "archive_location": str(ARCHIVE_ROOT.relative_to(PROJECT_ROOT)),
        "servers_archived": len(archived),
        "errors_encountered": len(errors),
        "archived_servers": archived,
        "errors": errors,
        "consolidation_plan": "Removing 8 servers as per FINAL_REMOVAL_LIST_FINAL.md"
    }
    
    # Save JSON report
    report_path = ARCHIVE_ROOT / "archive_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Save markdown report
    md_report_path = PROJECT_ROOT / "SERVER_ARCHIVE_REPORT.md"
    with open(md_report_path, 'w') as f:
        f.write(f"# Server Archive Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Summary\n")
        f.write(f"- Servers archived: {len(archived)}\n")
        f.write(f"- Errors encountered: {len(errors)}\n")
        f.write(f"- Archive location: `{report['archive_location']}`\n\n")
        
        f.write("## Archived Servers\n")
        for item in archived:
            f.write(f"- **{item['server']}**: `{item['from']}` → `{item['to']}`\n")
            if 'note' in item:
                f.write(f"  - Note: {item['note']}\n")
        
        if errors:
            f.write("\n## Errors\n")
            for error in errors:
                f.write(f"- {error}\n")
        
        f.write("\n## Next Steps\n")
        f.write("1. Update claude_desktop_config.json to remove references to archived servers\n")
        f.write("2. Update documentation to reflect the consolidation\n")
        f.write("3. Test remaining servers to ensure everything works\n")
        f.write("4. Delete ClaudeDesktopAgent directory if no longer needed\n")
    
    return report_path, md_report_path

def main():
    """Main archival function."""
    print("Server Consolidation - Archiving Redundant Servers")
    print("=" * 50)
    
    print(f"\nCreating archive at: {ARCHIVE_ROOT.relative_to(PROJECT_ROOT)}")
    create_archive_structure()
    
    print("\nArchiving servers...")
    archived, errors = archive_servers()
    
    print("\nCreating archive report...")
    json_report, md_report = create_archive_report(archived, errors)
    
    print(f"\nArchive complete!")
    print(f"- Archived {len(archived)} servers")
    print(f"- Encountered {len(errors)} errors")
    print(f"- JSON report: {json_report.relative_to(PROJECT_ROOT)}")
    print(f"- Markdown report: {md_report.relative_to(PROJECT_ROOT)}")
    
    if errors:
        print("\n⚠️ Some servers could not be archived. Check the report for details.")
    else:
        print("\n✅ All servers archived successfully!")

if __name__ == "__main__":
    main()