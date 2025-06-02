# Computer Use API Compliance Research

## 🔍 **Anthropic Computer Use Tool Specifications**

### **Tool Naming and Versions**

#### **Claude 4 (Latest)**
- `computer_20250124` - Enhanced computer control with improved precision
- `text_editor_20250429` - Updated text editor (NO undo_edit command)
- `bash_20250124` - Enhanced bash shell with improved capabilities
- **Beta Header Required**: `"anthropic-beta: computer-use-2025-01-24"`

#### **Claude Sonnet 3.7**
- `computer_20250124` - Includes new actions for more precise control
- `text_editor_20250124` - Same capabilities as 20241022 version
- `bash_20250124` - Same capabilities as 20241022 version

#### **Claude Sonnet 3.5 (new)**
- `computer_20241022` - Original computer tool
- `text_editor_20241022` - Original text editor tool
- `bash_20241022` - Original bash tool

### **Computer Tool Schema Analysis**

#### **Enhanced Actions (20250124)**
```python
actions = [
    "key",              # Press key combinations
    "hold_key",         # NEW: Hold keys for duration
    "type",             # Type text
    "cursor_position",  # Get cursor position
    "mouse_move",       # Move cursor
    "left_mouse_down",  # NEW: Press left button
    "left_mouse_up",    # NEW: Release left button
    "left_click",       # Click at coordinates
    "left_click_drag",  # Drag between coordinates
    "right_click",      # Right click
    "middle_click",     # Middle click
    "double_click",     # Double click
    "triple_click",     # NEW: Triple click
    "scroll",           # NEW: Scroll with direction/amount
    "wait",             # NEW: Wait for duration
    "screenshot",       # Take screenshot
]
```

#### **Required Parameters**
- `display_width_px`: **Required** - Screen width in pixels
- `display_height_px`: **Required** - Screen height in pixels  
- `display_number`: **Optional** - Display number (X11 environments)

#### **Tool Input Schema**
```python
{
    "properties": {
        "action": {
            "type": "string",
            "enum": [...actions...]
        },
        "coordinate": {
            "type": "array",
            "description": "(x, y) coordinates"
        },
        "start_coordinate": {
            "type": "array", 
            "description": "Start coords for drag"
        },
        "text": {
            "type": "string",
            "description": "Text for type/key actions"
        },
        "duration": {
            "type": "integer",
            "description": "Duration for hold_key/wait"
        },
        "scroll_direction": {
            "type": "string",
            "enum": ["up", "down", "left", "right"]
        },
        "scroll_amount": {
            "type": "integer",
            "description": "Number of scroll clicks"
        }
    },
    "required": ["action"],
    "type": "object"
}
```

## 🎯 **Implementation Requirements**

### **Our Current vs Required Tool Names**
```python
# CURRENT (our custom names)
current_tools = [
    "capture_screenshot",
    "click_coordinate", 
    "type_text",
    "get_mouse_position",
    "execute_powershell",
    "execute_wsl_command"
]

# REQUIRED (Computer Use API names)
required_tools = [
    "computer_20250124",      # All-in-one computer control
    "text_editor_20250429",   # File editing
    "bash_20250124"          # WSL command execution
]
```

### **Key Changes Needed**

1. **Consolidate Tools**: Replace multiple tools with single `computer_20250124` tool
2. **Update Action Schema**: Support all new enhanced actions
3. **Add Missing Actions**: `hold_key`, `triple_click`, `scroll`, `wait`, etc.
4. **Text Editor Tool**: Implement proper text editor with file operations
5. **Bash Tool**: Enhance WSL command execution

### **Tool Behavior Requirements**

#### **Computer Tool**
- Must handle screenshots, mouse, keyboard, scrolling, waiting
- Support enhanced precision actions (mouse_down/up, hold_key)
- Proper coordinate handling for all screen resolutions
- Wait functionality for application loading

#### **Text Editor Tool**
- File viewing, creating, editing operations
- Persistent state across command calls
- No `undo_edit` command in latest version (20250429)

#### **Bash Tool**
- WSL command execution with proper output capture
- Environment management and path handling

## 📋 **Next Steps**

### **Phase 1.2: Update Server Implementation**
1. **Rename Tools** - Update tool names to match Computer Use API
2. **Consolidate Actions** - Combine multiple tools into single computer tool
3. **Add Enhanced Actions** - Implement new actions (hold_key, scroll, wait, etc.)
4. **Update Schemas** - Match exact parameter schemas
5. **Test Compatibility** - Verify tools work with Claude Desktop

### **Phase 1.3: Test Integration**
1. **Restart Claude Desktop** - Load updated server configuration
2. **Test Basic Actions** - Screenshot, click, type, scroll
3. **Test Enhanced Actions** - hold_key, triple_click, wait
4. **Validate Responses** - Ensure response format matches expectations

## ✅ **Success Criteria**

- [ ] Tools named exactly as Computer Use API specification
- [ ] All enhanced actions implemented and functional
- [ ] Proper parameter handling for all action types
- [ ] Claude Desktop recognizes tools as Computer Use compatible
- [ ] Screenshot and automation working through Computer Use API

---

*This research forms the foundation for updating our Windows Computer Use MCP Server to be fully Computer Use API compliant.*