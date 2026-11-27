#!/usr/bin/env python3
"""
Final verification of AgenticSeek MCP setup
"""

import json
import os
import subprocess
import asyncio
import httpx

def check_agenticseek_api():
    """Check if AgenticSeek API is running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_mcp_server_files():
    """Check if all MCP server files exist"""
    server_dir = "C:\\AI_Projects\\Claude-MCP-tools\\servers\\agenticseek-mcp"
    required_files = [
        os.path.join(server_dir, "server_fastmcp.py"),
        os.path.join(server_dir, ".venv", "Scripts", "python.exe"),
        os.path.join(server_dir, "requirements.txt")
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

def check_claude_config():
    """Check Claude Desktop configuration"""
    config_path = "C:\\Users\\YOUR_USERNAME\\AppData\\Roaming\\Claude\\claude_desktop_config.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "agenticseek-mcp" in config.get("mcpServers", {}):
            agenticseek_config = config["mcpServers"]["agenticseek-mcp"]
            uses_fastmcp = "server_fastmcp.py" in str(agenticseek_config.get("args", []))
            return True, uses_fastmcp
        else:
            return False, False
    except:
        return False, False

def main():
    print("🔍 AgenticSeek MCP Final Verification")
    print("=" * 50)
    
    # Check 1: AgenticSeek API
    api_running = check_agenticseek_api()
    print(f"1. AgenticSeek API Running: {'✅ YES' if api_running else '❌ NO'}")
    
    # Check 2: MCP Server Files
    files_exist, missing = check_mcp_server_files()
    print(f"2. MCP Server Files: {'✅ ALL PRESENT' if files_exist else '❌ MISSING FILES'}")
    if missing:
        for file in missing:
            print(f"   Missing: {file}")
    
    # Check 3: Claude Configuration
    config_exists, uses_fastmcp = check_claude_config()
    print(f"3. Claude Desktop Config: {'✅ CONFIGURED' if config_exists else '❌ NOT CONFIGURED'}")
    print(f"4. Uses FastMCP Version: {'✅ YES' if uses_fastmcp else '❌ NO'}")
    
    # Overall Status
    all_good = api_running and files_exist and config_exists and uses_fastmcp
    
    print("\\n" + "=" * 50)
    if all_good:
        print("🎉 ALL SYSTEMS GO!")
        print("\\n📋 Next Steps:")
        print("   1. Restart Claude Desktop application")
        print("   2. Test with: 'Use smart_routing to analyze this text: Hello world'")
        print("   3. Try: 'Get provider status to see available AI models'")
        print("   4. Test: 'Use local_reasoning for private analysis of sensitive data'")
        print("\\n🎯 Smart Routing Priorities:")
        print("   • cost     → Local DeepSeek (free)")
        print("   • privacy  → Local DeepSeek (private)")
        print("   • speed    → OpenAI GPT-3.5 (fast)")
        print("   • quality  → OpenAI GPT-4 (best results)")
        print("   • balanced → Auto-select based on content")
    else:
        print("❌ ISSUES FOUND")
        print("\\nIssues to fix:")
        if not api_running:
            print("   • Start AgenticSeek: cd /mnt/c/AI_Projects/agenticSeek && ./agentic_seek_env/Scripts/python.exe api.py")
        if not files_exist:
            print("   • Missing MCP server files")
        if not config_exists:
            print("   • Add agenticseek-mcp to Claude Desktop config")
        if not uses_fastmcp:
            print("   • Update config to use server_fastmcp.py")

if __name__ == "__main__":
    main()
