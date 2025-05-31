# 🧪 Vibe Test Server - Testing Guide

## Setup Instructions

1. **Install Dependencies** (Run in Command Prompt):
   ```bash
   cd C:\AI_Projects\Claude-MCP-tools\servers\vibetest-use
   install_dependencies.bat
   ```

2. **Get Google API Key**:
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key
   - Copy the key

3. **Update Claude Config**:
   - Replace `YOUR_GOOGLE_API_KEY_HERE` in Claude Desktop config with your actual API key
   - Restart Claude Desktop

## Testing Prompts

### 🚀 Basic Website Testing
```
Test the website https://example.com for UI bugs and issues using 3 agents
```

### 🎯 Specific Site Testing
```
Run a vibe test on https://github.com with 5 agents to check for any broken functionality
```

### 🏢 E-commerce Testing
```
Test https://amazon.com homepage for accessibility and functionality issues using 4 agents
```

### 📱 Mobile-Friendly Testing
```
Run a comprehensive UI test on https://mobile.twitter.com with 3 agents focusing on responsive design
```

### 🔍 Deep Testing
```
Perform an extensive QA test on https://news.ycombinator.com using 6 agents to identify any broken links or UI problems
```

### ⚡ Quick Test
```
Do a quick vibe check on https://google.com with 2 agents
```

## Results Analysis Prompts

### 📊 Get Test Results
```
Show me the results for test ID [test_id_from_previous_run]
```

### 🔍 Detailed Analysis
```
Get the detailed bug report for test [test_id] and explain the severity of each issue found
```

## Advanced Usage

### 🎪 Custom Testing Scenarios
```
Test https://reddit.com for:
- Navigation functionality 
- Form submission capabilities
- Comment system usability
- Search feature reliability
Use 4 agents and provide detailed severity breakdown
```

### 🏗️ Development Site Testing
```
Run a comprehensive test suite on my development site at http://localhost:3000 using 3 agents to catch any issues before deployment
```

### 📈 Performance Testing
```
Test https://wikipedia.org for any slow-loading elements or broken functionality using 5 agents, then analyze the results for performance insights
```

## Expected Output Format

The vibe test will return:
- **Test ID**: Unique identifier for tracking
- **Overall Status**: ✅ Passing / 🟡 Minor Issues / 🟠 Moderate Issues / 🔴 Critical Issues
- **Severity Breakdown**: High/Medium/Low severity issues with specific descriptions
- **Agent Results**: Individual agent findings and test coverage
- **Duration**: Time taken to complete the test

## Troubleshooting

If tests fail to start:
1. Verify GOOGLE_API_KEY is set correctly
2. Check that dependencies are installed
3. Ensure the target website is accessible
4. Try with fewer agents (2-3) if experiencing resource issues

## Tips for Better Results

- **Start with 3 agents** for balanced coverage and speed
- **Use specific URLs** rather than general domains
- **Test after major site updates** to catch regressions
- **Run tests on both desktop and mobile-optimized sites**
- **Check results immediately** after test completion for best analysis

Happy testing! 🎉
