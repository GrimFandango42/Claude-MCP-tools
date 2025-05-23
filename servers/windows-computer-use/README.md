# Windows Computer Use MCP Server

## Overview

This MCP server provides Claude Computer Use capabilities adapted for Windows environments with WSL integration. It bridges the gap between Anthropic's Linux-focused Computer Use tools and Windows desktop automation.

## Architecture

### Core Components

1. **Windows Screenshot Capture** - Native Windows API screenshot functionality
2. **Windows Automation** - Mouse/keyboard automation using Windows APIs  
3. **WSL Bridge** - Integration with Windows Subsystem for Linux
4. **Security Sandbox** - Isolated execution environment for safe automation

### Windows-First Design

Unlike the reference Linux implementation, this server is designed Windows-first:

- **Primary Environment**: Windows 11 with native GUI automation
- **Development Bridge**: WSL2 integration for command-line tasks
- **Security Model**: Windows security contexts and process isolation
- **Display Handling**: Windows multi-monitor support with coordinate mapping

## Tools Provided

### 1. Computer Use Tool (`windows_computer_20250124`)
- **Screenshot Capture**: Multi-monitor Windows screenshot with coordinate mapping
- **Mouse Control**: Click, drag, scroll operations using Windows APIs
- **Keyboard Input**: Text input and key combinations via Windows input simulation
- **Window Management**: Focus, resize, minimize/maximize windows

### 2. Text Editor Tool (`windows_text_editor_20250429`) 
- **File Operations**: Read, write, edit text files on Windows filesystem
- **VSCode Integration**: Direct integration with VS Code on Windows
- **Path Translation**: Automatic Windows/WSL path translation

### 3. PowerShell Tool (`windows_powershell_20250124`)
- **Command Execution**: PowerShell command execution with output capture
- **WSL Bridge**: Execute Linux commands via WSL with proper environment setup
- **Environment Management**: Switch between Windows and WSL contexts

### 4. WSL Integration Tool (`wsl_bridge_20250124`)
- **File Synchronization**: Automatic file sync between Windows and WSL
- **Command Translation**: Translate Windows operations to WSL equivalents
- **Development Workflows**: VS Code, git, and development tool integration

## Implementation Phases

### Phase 1: Foundation (Current)
- [x] Project structure setup
- [ ] Windows screenshot capture implementation
- [ ] Basic mouse/keyboard automation
- [ ] MCP server protocol implementation

### Phase 2: WSL Integration 
- [ ] WSL command execution bridge
- [ ] File system path translation
- [ ] Environment context switching

### Phase 3: Advanced Features
- [ ] Application-specific automation (VS Code, browsers)
- [ ] Vision-guided element targeting
- [ ] Complex workflow orchestration

## Security Considerations

### Windows Security Model
- **Process Isolation**: Run automation in separate security contexts
- **Privilege Limitation**: Minimal required permissions for automation
- **Network Restrictions**: Limited network access for sandboxed operations

### WSL Security Bridge
- **File System Boundaries**: Controlled access between Windows and WSL filesystems
- **Command Validation**: Sanitize and validate all WSL commands
- **Resource Limits**: CPU and memory constraints for WSL operations

## Development Setup

### Prerequisites
- Windows 11 with WSL2 enabled
- PowerShell 7+ 
- Visual Studio Code with WSL extension
- Python 3.10+ for MCP server implementation

### Installation
```powershell
# Clone and setup
cd C:\AI_Projects\Claude-MCP-tools\servers\windows-computer-use
pip install -r requirements.txt

# Configure Claude Desktop
# Add server configuration to claude_desktop_config.json
```

## Usage Examples

### Basic Screenshot and Click
```python
# Take screenshot of current desktop
screenshot = await computer_use.screenshot()

# Click at coordinates (500, 300)
await computer_use.click(500, 300)
```

### WSL Integration
```python
# Execute command in WSL
result = await wsl_bridge.execute("ls -la /mnt/c/Users")

# Edit file in WSL context
await wsl_bridge.edit_file("/home/user/script.sh", content)
```

### Development Workflow
```python
# Open VS Code to specific project
await computer_use.open_application("code", "C:\\Projects\\MyApp")

# Switch to WSL terminal in VS Code
await computer_use.key_combination("ctrl+shift+`")

# Execute build command in WSL
await wsl_bridge.execute("npm run build")
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Desktop                           │
│                   (MCP Client)                              │
└─────────────────────┬───────────────────────────────────────┘
                      │ JSON-RPC over STDIO
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Windows Computer Use MCP Server                │
│  ┌─────────────────┬─────────────────┬─────────────────────┐ │
│  │   Screenshot    │   Automation    │   WSL Bridge        │ │
│  │   Capture       │   Engine        │   Controller        │ │
│  └─────────────────┴─────────────────┴─────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Windows Environment                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Windows GUI   │  │   PowerShell    │  │     WSL2    │  │
│  │   Applications  │  │   Commands      │  │  Linux Env  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Implement Core Tools**: Start with screenshot and basic automation
2. **Test Integration**: Validate with Claude Desktop 
3. **Add WSL Bridge**: Build Linux command execution capability
4. **Security Hardening**: Implement isolation and sandboxing
5. **Advanced Features**: Add vision-guided automation and complex workflows

This implementation leverages our existing MCP infrastructure while providing Windows-native Computer Use capabilities that complement Claude's Linux-focused reference implementation.