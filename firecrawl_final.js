#!/usr/bin/env node

/**
 * Simplified Firecrawl MCP Server
 * Focused on reliable stdin/stdout handling
 */

// Use readline for reliable line-by-line processing
const readline = require('readline');

// Log to stderr only to keep stdout clean for JSON-RPC
function log(msg) {
  console.error(`[${new Date().toISOString()}] ${msg}`);
}

log('Starting Firecrawl MCP Server');

// IMPORTANT: This configuration prevents readline from closing
// when it reaches the end of the input stream
const rl = readline.createInterface({
  input: process.stdin,
  output: null,  // Don't use readline for output to avoid mangling JSON
  terminal: false,
  historySize: 0,
  crlfDelay: Infinity
});

// Handle each line of input separately
rl.on('line', (line) => {
  try {
    // Only process non-empty lines
    if (line.trim() === '') return;
    
    log(`Received raw message: ${line}`);
    const message = JSON.parse(line);
    log(`Processing method: ${message.method} (id: ${message.id})`);
    
    // Handle message based on method
    handleJsonRpcMessage(message);
  } catch (err) {
    log(`Error processing message: ${err.message}`);
  }
});

// Keep the interface active even if stdin ends
rl.on('close', () => {
  log('Stdin closed but keeping server alive');
});

// Continue processing even after errors
rl.on('error', (err) => {
  log(`Readline error: ${err.message}`);
});

// Handle JSON-RPC messages
function handleJsonRpcMessage(message) {
  switch (message.method) {
    case 'initialize':
      sendJsonRpcResponse(message.id, {
        capabilities: {
          firecrawlProvider: {
            scrapeProvider: true,
            searchProvider: true,
            extractProvider: true
          }
        },
        serverInfo: {
          name: 'firecrawl-final',
          version: '1.0.0'
        }
      });
      break;
      
    case 'firecrawl/scrape':
      const url = message.params?.url || 'https://example.com';
      sendJsonRpcResponse(message.id, {
        url: url,
        content: `This is placeholder content for ${url}`,
        formats: message.params?.formats || ['markdown'],
        timestamp: new Date().toISOString()
      });
      break;
      
    case 'firecrawl/search':
      const query = message.params?.query || '';
      sendJsonRpcResponse(message.id, {
        query: query,
        results: [
          {
            title: `Result for: ${query}`,
            url: `https://example.com/search?q=${encodeURIComponent(query)}`,
            description: 'This is a placeholder search result.'
          }
        ]
      });
      break;
      
    case 'shutdown':
      sendJsonRpcResponse(message.id, null);
      log('Received shutdown request but keeping the server alive');
      break;
      
    default:
      sendJsonRpcError(message.id, -32601, `Method not supported: ${message.method}`);
  }
}

// Send a JSON-RPC response
function sendJsonRpcResponse(id, result) {
  const response = {
    jsonrpc: '2.0',
    id: id,
    result: result
  };
  
  const responseJson = JSON.stringify(response);
  log(`Sending response: ${responseJson}`);
  
  // Write directly to stdout bypassing readline
  process.stdout.write(responseJson + '\n');
  log(`Response sent for id: ${id}`);
}

// Send a JSON-RPC error
function sendJsonRpcError(id, code, message) {
  const response = {
    jsonrpc: '2.0',
    id: id,
    error: {
      code: code,
      message: message
    }
  };
  
  const responseJson = JSON.stringify(response);
  log(`Sending error: ${responseJson}`);
  
  // Write directly to stdout bypassing readline
  process.stdout.write(responseJson + '\n');
  log(`Error sent for id: ${id}`);
}

// Keep Node.js event loop active with heartbeat
const heartbeatInterval = setInterval(() => {
  log('Server heartbeat');
}, 10000);

// Prevent the heartbeat interval from being garbage collected
heartbeatInterval.unref();

// Handle signals but don't exit
process.on('SIGINT', () => {
  log('Received SIGINT but keeping server alive');
});

process.on('SIGTERM', () => {
  log('Received SIGTERM but keeping server alive');
});

process.on('beforeExit', () => {
  log('Process before exit but keeping server alive');
});

process.on('exit', () => {
  log('Process exit');
});

// Prevent uncaught exceptions from crashing the process
process.on('uncaughtException', (err) => {
  log(`Uncaught exception: ${err.message}`);
});

process.on('unhandledRejection', (reason) => {
  log(`Unhandled rejection: ${reason}`);
});

log('Firecrawl MCP Server ready for requests');
