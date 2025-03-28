#!/usr/bin/env node

/**
 * Optimized Firecrawl MCP Server
 * With minimal logging and robust connection handling
 */

// Use controlled logging with levels
const LOG_LEVELS = {
  ERROR: 0,
  WARN: 1,
  INFO: 2,
  DEBUG: 3
};

// Set this to control log verbosity
const CURRENT_LOG_LEVEL = LOG_LEVELS.INFO;

function log(level, message) {
  if (level <= CURRENT_LOG_LEVEL) {
    const prefix = level === LOG_LEVELS.ERROR ? 'ERROR' :
                 level === LOG_LEVELS.WARN  ? 'WARN'  :
                 level === LOG_LEVELS.INFO  ? 'INFO'  : 'DEBUG';
    
    console.error(`[${new Date().toISOString()}] [${prefix}] ${message}`);
  }
}

log(LOG_LEVELS.INFO, 'Starting Optimized Firecrawl MCP Server');

// Set up readline for robust line processing
const readline = require('readline');
const rl = readline.createInterface({
  input: process.stdin,
  output: null,  // Don't use readline for output
  terminal: false
});

// Track connection state to avoid redundant logging
let connectionState = 'connected';
let lastEofTime = 0;
let eofCount = 0;

// Handle input lines
rl.on('line', (line) => {
  try {
    // Only process non-empty lines
    if (line.trim() === '') return;
    
    // Reset EOF tracking on successful message
    connectionState = 'connected';
    eofCount = 0;
    
    log(LOG_LEVELS.DEBUG, `Received message: ${line}`);
    const message = JSON.parse(line);
    log(LOG_LEVELS.INFO, `Processing method: ${message.method} (id: ${message.id})`);
    
    // Handle the message
    handleJsonRpcMessage(message);
  } catch (err) {
    log(LOG_LEVELS.ERROR, `Error processing message: ${err.message}`);
  }
});

// Handle connection close with limited logging
rl.on('close', () => {
  if (connectionState !== 'disconnected') {
    connectionState = 'disconnected';
    log(LOG_LEVELS.WARN, 'Connection closed but keeping server alive');
  }
});

// Set up handler for EOF with throttled logging
process.stdin.on('end', () => {
  const now = Date.now();
  
  // Only log EOF at most once per 60 seconds to reduce noise
  if (now - lastEofTime > 60000) {
    log(LOG_LEVELS.WARN, 'Received EOF on stdin, but keeping server alive');
    lastEofTime = now;
    eofCount = 0;
  } else if (eofCount < 3) {
    // Log just a few times between the time window
    log(LOG_LEVELS.DEBUG, 'Additional EOF received');
    eofCount++;
  }
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
          name: 'firecrawl-optimized',
          version: '1.0.0'
        }
      });
      break;
      
    case 'firecrawl/scrape':
      try {
        const url = message.params?.url || 'https://example.com';
        log(LOG_LEVELS.INFO, `Scraping URL: ${url}`);
        
        // Simulate web scraping result
        sendJsonRpcResponse(message.id, {
          url: url,
          content: `This is placeholder content for ${url}`,
          formats: message.params?.formats || ['markdown'],
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        log(LOG_LEVELS.ERROR, `Scrape error: ${error.message}`);
        sendJsonRpcError(message.id, -32603, `Internal scraping error: ${error.message}`);
      }
      break;
      
    case 'firecrawl/search':
      try {
        const query = message.params?.query || '';
        log(LOG_LEVELS.INFO, `Searching for: ${query}`);
        
        // Simulate search result
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
      } catch (error) {
        log(LOG_LEVELS.ERROR, `Search error: ${error.message}`);
        sendJsonRpcError(message.id, -32603, `Internal search error: ${error.message}`);
      }
      break;
      
    case 'shutdown':
      sendJsonRpcResponse(message.id, null);
      log(LOG_LEVELS.INFO, 'Received shutdown request but keeping the server alive');
      break;
      
    default:
      // Don't log errors for polling methods
      if (!['resources/list', 'prompts/list'].includes(message.method)) {
        log(LOG_LEVELS.WARN, `Method not supported: ${message.method}`);
      }
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
  
  process.stdout.write(JSON.stringify(response) + '\n');
  log(LOG_LEVELS.DEBUG, `Response sent for id: ${id}`);
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
  
  process.stdout.write(JSON.stringify(response) + '\n');
  log(LOG_LEVELS.DEBUG, `Error response sent for id: ${id}`);
}

// Very quiet heartbeat - no logging
setInterval(() => {}, 30000);

// Handle process signals but don't exit
process.on('SIGINT', () => {
  log(LOG_LEVELS.WARN, 'Received SIGINT but keeping server alive');
});

process.on('SIGTERM', () => {
  log(LOG_LEVELS.WARN, 'Received SIGTERM but keeping server alive');
});

// Prevent uncaught exceptions from crashing the process
process.on('uncaughtException', (err) => {
  log(LOG_LEVELS.ERROR, `Uncaught exception: ${err.message}`);
});

process.on('unhandledRejection', (reason) => {
  log(LOG_LEVELS.ERROR, `Unhandled rejection: ${reason}`);
});

log(LOG_LEVELS.INFO, 'Firecrawl MCP Server ready for requests');
