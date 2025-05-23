#!/usr/bin/env node
/**
 * Automated Tests for Test Automation MCP Server
 * 
 * This script automatically tests the Test Automation MCP server by sending
 * a series of JSON-RPC requests and validating the responses.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const TIMEOUT = 30000; // 30 seconds timeout for tests

// Launch the MCP server as a child process
console.log('Starting Test Automation MCP Server...');
const server = spawn('node', ['server.js'], {
  stdio: ['pipe', 'pipe', 'pipe'],
  windowsHide: true
});

// Track test results
let testsPassed = 0;
let testsFailed = 0;
let currentTest = '';
let testTimeout = null;
let requestId = 1;

// Store server output for debugging
let serverOutput = [];
server.stdout.on('data', (data) => {
  const output = data.toString().trim();
  serverOutput.push(`[stdout] ${output}`);
  
  try {
    const response = JSON.parse(output);
    handleResponse(response);
  } catch (err) {
    console.log(`Non-JSON output from server: ${output}`);
  }
});

server.stderr.on('data', (data) => {
  const output = data.toString().trim();
  serverOutput.push(`[stderr] ${output}`);
  console.log(`Server log: ${output}`);
});

server.on('error', (err) => {
  console.error('Failed to start server process:', err);
  process.exit(1);
});

server.on('exit', (code, signal) => {
  console.log(`Server process exited with code ${code} and signal ${signal}`);
  if (code !== 0) {
    console.error('Server terminated unexpectedly');
    process.exit(1);
  }
});

// Test cases
const tests = [
  {
    name: 'initialize',
    request: {
      jsonrpc: '2.0',
      id: () => requestId++,
      method: 'initialize',
      params: {
        clientName: 'test-client',
        clientVersion: '1.0.0',
        capabilities: {}
      }
    },
    validate: (response) => {
      return response.result && 
             response.result.name === 'test-automation-mcp' && 
             response.result.capabilities && 
             response.result.capabilities.tools;
    }
  },
  {
    name: 'launch_browser',
    request: {
      jsonrpc: '2.0',
      id: () => requestId++,
      method: 'launch_browser',
      params: {
        browserType: 'chromium',
        headless: true
      }
    },
    validate: (response) => {
      return response.result && response.result.success === true;
    }
  },
  {
    name: 'goto',
    request: {
      jsonrpc: '2.0',
      id: () => requestId++,
      method: 'goto',
      params: {
        url: 'https://example.com'
      }
    },
    validate: (response) => {
      return response.result && 
             response.result.success === true && 
             response.result.status === 200;
    }
  },
  {
    name: 'assert_element',
    request: {
      jsonrpc: '2.0',
      id: () => requestId++,
      method: 'assert_element',
      params: {
        selector: 'h1',
        state: 'visible',
        timeout: 5000
      }
    },
    validate: (response) => {
      return response.result && 
             response.result.success === true && 
             response.result.result === true;
    }
  },
  {
    name: 'capture_screenshot',
    request: {
      jsonrpc: '2.0',
      id: () => requestId++,
      method: 'capture_screenshot',
      params: {}
    },
    validate: (response) => {
      return response.result && 
             response.result.success === true && 
             response.result.path && 
             fs.existsSync(response.result.path);
    }
  },
  {
    name: 'get_performance_metrics',
    request: {
      jsonrpc: '2.0',
      id: () => requestId++,
      method: 'get_performance_metrics',
      params: {}
    },
    validate: (response) => {
      return response.result && 
             response.result.success === true && 
             response.result.metrics;
    }
  },
  {
    name: 'run_steps',
    request: {
      jsonrpc: '2.0',
      id: () => requestId++,
      method: 'run_steps',
      params: {
        steps: [
          { goto: 'https://playwright.dev' },
          { click: '.navbar__item:has-text("Docs")' },
          { screenshot: {} }
        ]
      }
    },
    validate: (response) => {
      return response.result && 
             response.result.status && 
             Array.isArray(response.result.steps) && 
             response.result.steps.length === 3;
    }
  },
  {
    name: 'close_browser',
    request: {
      jsonrpc: '2.0',
      id: () => requestId++,
      method: 'close_browser',
      params: {}
    },
    validate: (response) => {
      return response.result && response.result.success === true;
    }
  }
];

// Response handler
function handleResponse(response) {
  if (!currentTest) {
    console.log(`Unexpected response: ${JSON.stringify(response)}`);
    return;
  }
  
  // Find the test case for this response
  const test = tests.find(t => t.name === currentTest);
  if (!test) {
    console.log(`No test found for ${currentTest}`);
    return;
  }
  
  // Clear timeout
  if (testTimeout) {
    clearTimeout(testTimeout);
    testTimeout = null;
  }
  
  // Validate response
  try {
    if (test.validate(response)) {
      console.log(`✅ Test '${test.name}' PASSED`);
      testsPassed++;
    } else {
      console.log(`❌ Test '${test.name}' FAILED: Invalid response`);
      console.log(`Response: ${JSON.stringify(response, null, 2)}`);
      testsFailed++;
    }
  } catch (err) {
    console.log(`❌ Test '${test.name}' FAILED: ${err.message}`);
    console.log(`Response: ${JSON.stringify(response, null, 2)}`);
    testsFailed++;
  }
  
  // Run next test
  currentTest = '';
  runNextTest();
}

// Send a request to the server
function sendRequest(request) {
  const finalRequest = { ...request };
  if (typeof finalRequest.id === 'function') {
    finalRequest.id = finalRequest.id();
  }
  
  server.stdin.write(JSON.stringify(finalRequest) + '\n');
}

// Run tests sequentially
function runNextTest() {
  // Get the index of the next test
  const currentIndex = currentTest ? tests.findIndex(t => t.name === currentTest) : -1;
  const nextIndex = currentIndex + 1;
  
  if (nextIndex >= tests.length) {
    // All tests completed
    finishTests();
    return;
  }
  
  const test = tests[nextIndex];
  console.log(`Running test: ${test.name}`);
  currentTest = test.name;
  
  // Set timeout
  testTimeout = setTimeout(() => {
    console.log(`❌ Test '${test.name}' FAILED: Timeout after ${TIMEOUT/1000} seconds`);
    testsFailed++;
    currentTest = '';
    runNextTest();
  }, TIMEOUT);
  
  // Send request
  sendRequest(test.request);
}

// Finish testing and report results
function finishTests() {
  const total = testsPassed + testsFailed;
  
  console.log('\n==================================');
  console.log(`Test Summary: ${testsPassed}/${total} tests passed`);
  console.log('==================================');
  
  if (testsFailed > 0) {
    console.log(`\n⚠️ ${testsFailed} test(s) failed!`);
  } else {
    console.log('\n🎉 All tests passed!');
  }
  
  // Kill the server process
  server.kill();
  
  // Exit with success only if all tests passed
  process.exit(testsFailed > 0 ? 1 : 0);
}

// Start testing
runNextTest();