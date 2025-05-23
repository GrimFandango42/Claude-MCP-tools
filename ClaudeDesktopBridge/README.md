# Claude Desktop Bridge

A framework for extending Claude for Desktop with advanced computer control capabilities using the Anthropic Computer Use API.

## Overview

Claude Desktop Bridge provides a seamless integration between Claude for Desktop and various computer control functionalities. It enables Claude to interact with your desktop environment, perform tasks, and utilize various automation features.

## Features

- **Computer Control**: Capture screenshots, perform mouse clicks, type text, press keys, move the mouse, scroll, and perform drag operations.
- **Browser Automation**: Navigate to URLs, click on elements, type text, extract content, perform web searches, and take screenshots of web pages.
- **System Integration**: Execute system commands, launch applications, list installed applications, get system information, and monitor running processes.
- **Tools Registry**: Register, list, and manage available tools for Claude to use.
- **Bridge API**: Connect Claude for Desktop with the computer control capabilities via a RESTful API.

## Architecture

The framework follows a modular architecture with the following components:

```
ClaudeDesktopBridge/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── bridge.py     # Bridge between Claude and computer control
│   │   │   ├── browser.py    # Browser automation endpoints
│   │   │   ├── computer.py   # Computer control endpoints
│   │   │   ├── system.py     # System integration endpoints
│   │   │   └── tools.py      # Tools registry endpoints
│   │   └── router.py         # Main API router
│   ├── modules/
│   │   ├── bridge.py         # Bridge module implementation
│   │   ├── browser.py        # Browser module implementation
│   │   ├── computer.py       # Computer module implementation
│   │   └── system.py         # System module implementation
│   ├── utils/
│   │   ├── config.py         # Configuration settings
│   │   ├── logger.py         # Logging utility
│   │   └── security.py       # Security utility
│   └── main.py               # Main application entry point
├── logs/                     # Log files
├── screenshots/              # Screenshot storage
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
└── README.md                 # Documentation
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Anthropic API key (for Claude integration)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ClaudeDesktopBridge.git
cd ClaudeDesktopBridge
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content:

```
ANTHROPIC_API_KEY=your_anthropic_api_key
API_KEY=your_api_key_for_security
PORT=8000
DEBUG=True
```

### Running the Application

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Computer Control

- `POST /api/computer/screenshot`: Capture a screenshot
- `POST /api/computer/click`: Perform a mouse click
- `POST /api/computer/type`: Type text
- `POST /api/computer/key_press`: Press a key
- `POST /api/computer/mouse_move`: Move the mouse
- `POST /api/computer/scroll`: Scroll the mouse wheel
- `POST /api/computer/drag`: Perform a drag operation

### Browser Automation

- `POST /api/browser/navigate`: Navigate to a URL
- `POST /api/browser/click`: Click on an element
- `POST /api/browser/type`: Type text into an element
- `POST /api/browser/extract`: Extract content from the page
- `POST /api/browser/search`: Perform a web search
- `POST /api/browser/screenshot`: Take a screenshot of the page

### System Integration

- `POST /api/system/execute`: Execute a system command
- `POST /api/system/launch`: Launch an application
- `GET /api/system/applications`: List installed applications
- `GET /api/system/info`: Get system information
- `GET /api/system/processes`: Get running processes

### Tools Registry

- `GET /api/tools/list`: List all available tools
- `GET /api/tools/{tool_id}`: Get details for a specific tool
- `POST /api/tools/register`: Register a new tool
- `DELETE /api/tools/{tool_id}`: Unregister a tool

### Bridge API

- `POST /api/bridge/tool_use`: Handle a tool use request from Claude
- `POST /api/bridge/message`: Send a message to Claude API with tools enabled
- `POST /api/bridge/webhook`: Webhook endpoint for Claude for Desktop
- `GET /api/bridge/status`: Get the status of the bridge

## Security Considerations

- The framework includes API key authentication to secure the endpoints.
- Only allowed commands and applications can be executed to prevent security risks.
- Logging and error handling are implemented to ensure that any issues are recorded and can be diagnosed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Anthropic](https://www.anthropic.com/) for the Claude API
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [PyAutoGUI](https://pyautogui.readthedocs.io/) for computer control
- [Selenium](https://www.selenium.dev/) for browser automation
