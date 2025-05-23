# Test Automation MCP Server

A Model Context Protocol server for end-to-end test automation using Playwright, Puppeteer, and complementary tools. This server enables Claude Desktop to perform browser automation, run test suites, and capture various test artifacts.

## Features

- **Full Browser Automation**: Launch and control Chromium, Firefox, and WebKit browsers
- **Advanced Test Capabilities**: Run structured test steps, assert element states, capture screenshots
- **Performance Metrics**: Collect core web vitals and performance data
- **Artifact Management**: Organize and store screenshots, videos, and test reports
- **100% Local Operation**: All testing happens locally with no external dependencies

## Setup

### Prerequisites

- Node.js 14+ and npm
- Windows OS (optimized for Claude Desktop on Windows)

### Installation

1. Clone or download this repository
2. Navigate to the project directory:
   ```
   cd C:\AI_Projects\Claude-MCP-tools\servers\test-automation-mcp
   ```
3. Install dependencies:
   ```
   npm install
   ```
4. Install Playwright browsers:
   ```
   npx playwright install --with-deps chromium
   ```

### Claude Desktop Integration

Add the following to your Claude Desktop configuration file (`C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json`):

```json
{
  "name": "test-automation",
  "command": "cmd",
  "args": [
    "/c",
    "set PLAYWRIGHT_BROWSERS_PATH=0 && npx -y @modelcontextprotocol/test-automation-mcp"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

Alternatively, for local development without npm publishing, use the batch file approach:

```json
{
  "name": "test-automation",
  "command": "C:\\AI_Projects\\Claude-MCP-tools\\servers\\test-automation-mcp\\run-test-automation-mcp.bat",
  "keepAlive": true,
  "stderrToConsole": true
}
```

## Tools & Capabilities

### Browser Management

- `launch_browser`: Start a new browser instance (chromium, firefox, webkit)
- `close_browser`: Close the active browser
- `list_browsers`: List available browser engines

### Page Interaction

- `goto`: Navigate to a URL
- `click`: Click an element
- `fill`: Fill in a form field
- `assert_element`: Verify element state (visible, hidden, enabled)

### Test Artifacts

- `capture_screenshot`: Take a screenshot of the page or element
- `get_performance_metrics`: Collect performance data

### Test Suite Execution

- `run_steps`: Execute a sequence of test steps

## Example Usage

```yaml
# Sample test suite (YAML format)
name: Login Flow Test
browser: chromium
headless: true

steps:
  - goto: "https://example.com/login"
  - fill:
      selector: "#username"
      value: "testuser"
  - fill:
      selector: "#password"
      value: "password123"
  - click: "button[type=submit]"
  - assert:
      selector: ".welcome-message"
      state: "visible"
      timeout: 5000
  - screenshot: {}
```

## Architecture

The server follows the Model Context Protocol specification, communicating over stdin/stdout using JSON-RPC. Key components:

- **Core Server**: Node.js-based JSON-RPC server with MCP implementation
- **Playwright Integration**: Browser automation engine
- **Artifact Storage**: Local storage for test artifacts
- **Signal Handling**: Graceful shutdown and cleanup

## Troubleshooting

### Common Issues

- **Browser launch fails**: Ensure Playwright browsers are installed with `npx playwright install`
- **Permission errors**: Check that artifact directories are writable
- **Connection issues**: Verify Claude Desktop configuration has `keepAlive: true`

### Logs

Check the logs in:
- `C:\Users\<YourUsername>\AppData\Roaming\Claude\logs\mcp-server-test-automation.log`

## Future Enhancements

- WinAppDriver integration for native Windows application testing
- Lighthouse integration for performance audits
- Visual comparison features
- Test report generation
- Parallel test execution

## Contributing

Contributions are welcome! Please follow the standard GitHub workflow:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT