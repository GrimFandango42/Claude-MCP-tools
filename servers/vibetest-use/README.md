# Vibetest Use MCP Server

An MCP server that launches multiple Browser-Use agents to test a vibe-coded website for UI bugs, broken links, accessibility issues, and other technical problems.

Perfect for testing both live websites and localhost development sites. Vibecode and vibetest until your website works!

## Features

- **Multi-Agent Testing**: Deploy multiple browser agents simultaneously to test different parts of your website
- **Intelligent Scouting**: AI scouts the website first to identify interactive elements and create targeted test tasks
- **Comprehensive Analysis**: Uses Google's Gemini models for detailed issue analysis and severity classification
- **Flexible Deployment**: Supports both headless and visual testing modes
- **Real-time Results**: Get detailed reports with specific issue descriptions and severity ratings

## Prerequisites

- **Python 3.11+**
- **Google API Key** ([get one here](https://developers.google.com/maps/api-security-best-practices))
- **Claude Desktop with MCP support** or **Claude Code CLI**

## Installation

1. **Clone and Install Dependencies**:
   ```bash
   cd C:/AI_Projects/Claude-MCP-tools/servers/vibetest-use
   
   # Create virtual environment
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On Linux/Mac
   
   # Install dependencies
   pip install -e .
   
   # Install Playwright browsers
   playwright install
   ```

2. **Get Google API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key
   - Save it for the MCP configuration

## Configuration

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vibetest": {
      "command": "C:/AI_Projects/Claude-MCP-tools/servers/vibetest-use/.venv/Scripts/python.exe",
      "args": ["-m", "vibetest.mcp_server"],
      "env": {
        "GOOGLE_API_KEY": "your_google_api_key_here"
      }
    }
  }
}
```

### Claude Code CLI Configuration

```bash
# Add MCP server via CLI
claude mcp add vibetest C:/AI_Projects/Claude-MCP-tools/servers/vibetest-use/.venv/Scripts/python.exe -a "-m" -a "vibetest.mcp_server" -e GOOGLE_API_KEY="your_api_key"

# Test in Claude Code
claude
/mcp
```

## Usage

### Available Tools

1. **start(url, num_agents=3, headless=False)**: Launch browser agents to test a website
   - `url`: Website URL to test (supports http/https/localhost)
   - `num_agents`: Number of QA agents to spawn (default: 3, max recommended: 10)
   - `headless`: Run browsers in headless mode (default: False for visual debugging)
   - Returns: `test_id` for tracking the test run

2. **results(test_id)**: Get consolidated bug report for a test run
   - `test_id`: The test ID returned from start()
   - Returns: Detailed analysis with severity classification

### Example Prompts

```
> Vibetest my website with 5 agents: https://example.com
> Run vibetest on localhost:3000
> Test my site with 3 agents in headless mode: https://mysite.dev
> Check the results for test ID abc-123-def
```

### Test Parameters

- **URL**: Any website (`https://example.com`, `localhost:3000`, `http://dev.mysite.com`)
- **Number of agents**: 3 (default), 5 agents, 2 agents - more agents = more thorough testing
- **Headless mode**: `false` (default for debugging) or `true` (for CI/automated testing)

## How It Works

1. **Scout Phase**: An AI agent first explores the website to catalog all interactive elements
2. **Task Generation**: The scout findings are processed to create specific test tasks for each agent
3. **Parallel Testing**: Multiple browser agents run simultaneously, each testing different website components
4. **Result Analysis**: Google's Gemini AI analyzes findings and classifies issues by severity
5. **Report Generation**: Consolidated report with actionable insights and specific bug descriptions

## Sample Output

```json
{
  "test_id": "abc-123-def",
  "overall_status": "medium-severity",
  "status_emoji": "🟠",
  "status_description": "Moderate issues found that should be addressed",
  "total_issues": 3,
  "successful_agents": 5,
  "failed_agents": 0,
  "duration_formatted": "2m 34s",
  "severity_breakdown": {
    "high_severity": [],
    "medium_severity": [
      {
        "category": "navigation",
        "description": "Upon clicking the 'Contact Us' link in the footer, the page redirected to a 404 error instead of the contact form"
      }
    ],
    "low_severity": [
      {
        "category": "forms",
        "description": "Newsletter signup form accepts empty email addresses without validation"
      }
    ]
  }
}
```

## Architecture

- **MCP Server**: FastMCP-based server exposing vibetest tools
- **Browser Agents**: browser-use library with Playwright for browser automation
- **AI Models**: Google Gemini for task generation and analysis
- **Async Architecture**: Parallel agent execution with semaphore-based concurrency control

## Advanced Features

### Smart Window Management
In non-headless mode, the system automatically positions browser windows in a grid layout to avoid overlap and provide visual debugging capabilities.

### Intelligent Task Distribution
The scout agent analyzes the website structure and creates targeted test tasks that are distributed among agents to avoid redundant testing.

### Severity Classification
Issues are automatically classified into three severity levels:
- 🔴 **High Severity**: Critical functionality breaks, security issues
- 🟠 **Medium Severity**: Important features not working properly
- 🟡 **Low Severity**: Minor issues, accessibility improvements

### Resource Management
Automatic cleanup of browser processes and memory management to prevent resource leaks during extensive testing.

## Troubleshooting

### Common Issues

1. **GOOGLE_API_KEY not set**: Ensure your API key is properly configured in the MCP server environment
2. **Playwright browsers not installed**: Run `playwright install` in your virtual environment
3. **Permission errors**: Ensure the Python executable path is correct in your MCP configuration
4. **Browser crashes**: Try running in headless mode or reducing the number of agents

### Debug Mode

For visual debugging, use `headless=false` to see the browser windows during testing:

```
> Run vibetest on localhost:3000 with 2 agents in non-headless mode
```

### Performance Tuning

- **Fewer agents**: Start with 3 agents for basic testing
- **More agents**: Use 5-10 agents for comprehensive testing (may slow down the target website)
- **Headless mode**: Use headless=true for faster execution in CI/automated environments

## Development

### Project Structure
```
vibetest-use/
├── vibetest/
│   ├── __init__.py
│   ├── mcp_server.py    # MCP server implementation
│   └── agents.py        # Browser agent orchestration
├── pyproject.toml       # Project configuration
└── README.md           # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with various websites
5. Submit a pull request

### Testing the MCP Server

```bash
# Activate virtual environment
.venv\Scripts\activate

# Test the server directly
python -m vibetest.mcp_server

# Test with Claude Desktop
# Add server to config and restart Claude Desktop
```

## Integration Examples

### CI/CD Pipeline
```yaml
- name: Install Vibetest
  run: |
    pip install -e ./servers/vibetest-use
    playwright install

- name: Run Website Tests
  env:
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  run: |
    claude mcp add vibetest ./servers/vibetest-use/.venv/bin/python -a "-m" -a "vibetest.mcp_server"
    # Run tests via Claude Code
```

### Local Development Workflow
```bash
# Start your development server
npm run dev  # or whatever starts your local server

# In Claude Desktop/Code:
# "Run vibetest on localhost:3000 with 5 agents"
# "Check results for the latest test"
```

## Limitations

- Requires Google API key and internet connection
- Browser-based testing may be slower than unit tests
- Limited to websites that can be automated (no CAPTCHA, complex auth)
- Concurrent testing may put load on target website

## Roadmap

- [ ] Support for additional AI providers (OpenAI, Anthropic)
- [ ] Custom test scenario scripting
- [ ] Integration with popular testing frameworks
- [ ] Screenshot capture for visual regression testing
- [ ] Performance metrics collection
- [ ] Accessibility compliance scoring

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs in Claude Desktop
3. Test with a simple website first
4. Ensure all dependencies are properly installed

---

*Powered by [Browser Use](https://github.com/browser-use/browser-use) and Claude MCP Framework*
