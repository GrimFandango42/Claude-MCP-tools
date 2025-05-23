#!/usr/bin/env node
/**
 * Test script for the Test Automation MCP Server
 * 
 * This script simulates the Claude Desktop MCP client to test the JSON-RPC
 * functionality of the test-automation-mcp server.
 */

const { spawn } = require('child_process');
const readline = require('readline');

// Launch the MCP server as a child process
const server = spawn('node', ['server.js'], {
  stdio: ['pipe', 'pipe', process.stderr],
  windowsHide: true
});

// Log any server errors
server.on('error', (err) => {
  console.error('Failed to start server process:', err);
  process.exit(1);
});

server.on('exit', (code, signal) => {
  console.log(`Server process exited with code ${code} and signal ${signal}`);
  process.exit(0);
});

// Create interface for sending commands
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

let requestId = 1;

// Handle server output
server.stdout.on('data', (data) => {
  try {
    const response = JSON.parse(data.toString());
    console.log('\nServer response:');
    console.log(JSON.stringify(response, null, 2));
    promptCommand();
  } catch (err) {
    console.error('Error parsing server response:', err);
    console.log('Raw response:', data.toString());
    promptCommand();
  }
});

// Send initialize message to server
function initialize() {
  const initRequest = {
    jsonrpc: '2.0',
    id: requestId++,
    method: 'initialize',
    params: {
      clientName: 'test-client',
      clientVersion: '1.0.0',
      capabilities: {}
    }
  };
  
  server.stdin.write(JSON.stringify(initRequest) + '\n');
}

// Send JSON-RPC request to server
function sendRequest(method, params) {
  const request = {
    jsonrpc: '2.0',
    id: requestId++,
    method,
    params
  };
  
  server.stdin.write(JSON.stringify(request) + '\n');
}

// Display available tools
function showHelp() {
  console.log('\nAvailable commands:');
  console.log('- launch : Launch a browser (params: browserType, headless)');
  console.log('- goto   : Navigate to a URL (params: url)');
  console.log('- click  : Click an element (params: selector)');
  console.log('- fill   : Fill a form field (params: selector, value)');
  console.log('- assert : Assert element state (params: selector, state, timeout)');
  console.log('- screenshot : Capture screenshot (params: selector?, path?)');
  console.log('- metrics : Get performance metrics');
  console.log('- close  : Close the browser');
  console.log('- steps  : Run a sequence of steps');
  console.log('- exit   : Exit the test client');
  console.log('- help   : Show this help message');
  promptCommand();
}

// Prompt for command
function promptCommand() {
  rl.question('\nEnter command (or "help"): ', (cmd) => {
    if (cmd === 'exit') {
      console.log('Exiting test client...');
      server.kill();
      rl.close();
      return;
    }
    
    if (cmd === 'help') {
      showHelp();
      return;
    }
    
    switch (cmd) {
      case 'launch':
        rl.question('Browser type [chromium]: ', (browserType) => {
          rl.question('Headless (true/false) [true]: ', (headless) => {
            sendRequest('launch_browser', {
              browserType: browserType || 'chromium',
              headless: headless !== 'false'
            });
          });
        });
        break;
        
      case 'goto':
        rl.question('URL: ', (url) => {
          sendRequest('goto', { url });
        });
        break;
        
      case 'click':
        rl.question('Selector: ', (selector) => {
          sendRequest('click', { selector });
        });
        break;
        
      case 'fill':
        rl.question('Selector: ', (selector) => {
          rl.question('Value: ', (value) => {
            sendRequest('fill', { selector, value });
          });
        });
        break;
        
      case 'assert':
        rl.question('Selector: ', (selector) => {
          rl.question('State (visible/hidden/enabled) [visible]: ', (state) => {
            rl.question('Timeout [5000]: ', (timeout) => {
              sendRequest('assert_element', {
                selector,
                state: state || 'visible',
                timeout: parseInt(timeout || '5000')
              });
            });
          });
        });
        break;
        
      case 'screenshot':
        rl.question('Selector (optional): ', (selector) => {
          rl.question('Path (optional): ', (path) => {
            sendRequest('capture_screenshot', {
              selector: selector || undefined,
              path: path || undefined
            });
          });
        });
        break;
        
      case 'metrics':
        sendRequest('get_performance_metrics', {});
        break;
        
      case 'close':
        sendRequest('close_browser', {});
        break;
        
      case 'steps':
        console.log('Enter a series of steps in JSON format:');
        console.log('Example: [{ "goto": "https://example.com" }, { "click": "#button" }]');
        rl.question('Steps: ', (stepsJson) => {
          try {
            const steps = JSON.parse(stepsJson);
            sendRequest('run_steps', { steps });
          } catch (err) {
            console.error('Invalid JSON:', err.message);
            promptCommand();
          }
        });
        break;
        
      default:
        console.log(`Unknown command: ${cmd}`);
        showHelp();
        break;
    }
  });
}

// Handle process termination
process.on('SIGINT', () => {
  console.log('\nExiting test client...');
  server.kill();
  rl.close();
  process.exit(0);
});

// Start the test client
console.log('Test Automation MCP Server Test Client');
console.log('====================================');
initialize();
showHelp();