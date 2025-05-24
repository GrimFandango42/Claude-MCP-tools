#!/usr/bin/env node

/**
 * N8n MCP Server Test Script
 * 
 * Tests the N8n MCP server functionality by sending test requests
 * and validating responses.
 */

import { spawn } from 'child_process';
import { setTimeout } from 'timers/promises';

// Test cases
const TEST_CASES = [
  {
    name: 'List Node Types',
    request: {
      jsonrpc: '2.0',
      id: 1,
      method: 'tools/call',
      params: {
        name: 'list_node_types',
        arguments: {}
      }
    }
  },
  {
    name: 'Generate Simple Workflow',
    request: {
      jsonrpc: '2.0',
      id: 2,
      method: 'tools/call',
      params: {
        name: 'generate_workflow',
        arguments: {
          description: 'Create a workflow that fetches data from an API and processes it',
          name: 'Test API Workflow'
        }
      }
    }
  },
  {
    name: 'Create Template Workflow',
    request: {
      jsonrpc: '2.0',
      id: 3,
      method: 'tools/call',
      params: {
        name: 'create_template',
        arguments: {
          template: 'basic-http-processing',
          name: 'Test Template Workflow'
        }
      }
    }
  },
  {
    name: 'Create Custom Workflow',
    request: {
      jsonrpc: '2.0',
      id: 4,
      method: 'tools/call',
      params: {
        name: 'create_custom_workflow',
        arguments: {
          name: 'Custom Test Workflow',
          description: 'A test workflow with custom configuration',
          nodes: [
            { type: 'Manual Trigger' },
            { type: 'HTTP Request', params: { name: 'Fetch Data' } },
            { type: 'Code', params: { name: 'Process Data' } }
          ],
          connections: [
            { from: 0, to: 1 },
            { from: 1, to: 2 }
          ]
        }
      }
    }
  }
];

async function runTest() {
  console.log('🚀 Starting N8n MCP Server Tests\\n');

  // Start the server
  const serverProcess = spawn('node', ['server.js'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: process.cwd()
  });

  let testResults = [];
  let testIndex = 0;

  // Handle server stderr (logs)
  serverProcess.stderr.on('data', (data) => {
    const logLines = data.toString().split('\\n').filter(line => line.trim());
    logLines.forEach(line => {
      try {
        const logEntry = JSON.parse(line);
        console.log(`[SERVER] ${logEntry.level.toUpperCase()}: ${logEntry.message}`);
      } catch (e) {
        console.log(`[SERVER] ${line}`);
      }
    });
  });

  // Handle server stdout (responses)
  serverProcess.stdout.on('data', (data) => {
    const responses = data.toString().split('\\n').filter(line => line.trim());
    
    responses.forEach(responseStr => {
      try {
        const response = JSON.parse(responseStr);
        const testCase = TEST_CASES.find(tc => tc.request.id === response.id);
        
        if (testCase) {
          const success = !response.error;
          testResults.push({
            name: testCase.name,
            success,
            response: success ? response.result : response.error
          });

          console.log(`\\n✅ Test: ${testCase.name}`);
          if (success) {
            console.log('   Status: PASSED');
            if (response.result.content && response.result.content[0]) {
              const content = response.result.content[0].text;
              console.log(`   Content Preview: ${content.substring(0, 200)}...`);
            }
          } else {
            console.log('   Status: FAILED');
            console.log(`   Error: ${response.error.message}`);
          }
        }
      } catch (e) {
        console.log(`[RESPONSE] ${responseStr}`);
      }
    });

    // Check if all tests completed
    if (testResults.length === TEST_CASES.length) {
      finishTests();
    }
  });

  // Initialize the server
  console.log('Initializing server...');
  const initRequest = {
    jsonrpc: '2.0',
    id: 0,
    method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: {
        name: 'test-client',
        version: '1.0.0'
      }
    }
  };

  serverProcess.stdin.write(JSON.stringify(initRequest) + '\\n');

  // Wait for initialization
  await setTimeout(2000);

  // Run test cases
  console.log('\\n🧪 Running test cases...\\n');
  for (const testCase of TEST_CASES) {
    console.log(`Running: ${testCase.name}`);
    serverProcess.stdin.write(JSON.stringify(testCase.request) + '\\n');
    await setTimeout(1000); // Wait between tests
  }

  // Set timeout for test completion
  setTimeout(() => {
    if (testResults.length < TEST_CASES.length) {
      console.log('\\n⚠️  Test timeout - not all tests completed');
      finishTests();
    }
  }, 30000);

  function finishTests() {
    console.log('\\n📊 Test Results Summary:');
    console.log('=' .repeat(50));
    
    const passed = testResults.filter(r => r.success).length;
    const failed = testResults.length - passed;
    
    testResults.forEach(result => {
      const status = result.success ? '✅ PASS' : '❌ FAIL';
      console.log(`${status} - ${result.name}`);
      if (!result.success && result.response) {
        console.log(`      Error: ${result.response.message || 'Unknown error'}`);
      }
    });
    
    console.log('\\n' + '='.repeat(50));
    console.log(`Total: ${testResults.length}, Passed: ${passed}, Failed: ${failed}`);
    
    if (failed === 0) {
      console.log('\\n🎉 All tests passed! The N8n MCP server is working correctly.');
    } else {
      console.log(`\\n⚠️  ${failed} test(s) failed. Please check the server implementation.`);
    }

    // Shutdown the server
    console.log('\\nShutting down server...');
    const shutdownRequest = {
      jsonrpc: '2.0',
      id: 999,
      method: 'shutdown',
      params: {}
    };
    
    serverProcess.stdin.write(JSON.stringify(shutdownRequest) + '\\n');
    
    setTimeout(() => {
      serverProcess.kill();
      process.exit(failed === 0 ? 0 : 1);
    }, 2000);
  }
}

// Handle process signals
process.on('SIGINT', () => {
  console.log('\\n🛑 Test interrupted');
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  console.error('\\n💥 Test error:', error.message);
  process.exit(1);
});

// Run the tests
runTest().catch(error => {
  console.error('💥 Failed to run tests:', error.message);
  process.exit(1);
});
