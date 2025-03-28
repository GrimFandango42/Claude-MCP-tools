#!/usr/bin/env node

/**
 * Firecrawl MCP Server - Core Implementation
 * Following official MCP standards with minimal complexity
 */

// Use stderr for logging to avoid corrupting the JSON-RPC protocol
function log(message) {
  console.error(`[${new Date().toISOString()}] ${message}`);
}

log('Starting Firecrawl MCP Server');

// Set up stdin for JSON-RPC communication
process.stdin.setEncoding('utf8');

// CRITICAL: We must read from stdin continuously to keep the process alive
let buffer = '';
process.stdin.on('data', (chunk) => {
  buffer += chunk;
  
  try {
    // Try to parse a complete JSON message
    const message = JSON.parse(buffer);
    buffer = ''; // Clear buffer on successful parse
    
    // Process the message
    handleMessage(message);
  } catch (err) {
    // Not a complete JSON object yet, keep buffering
  }
});

// Ensure process stays alive even when stdin ends
process.stdin.on('end', () => {
  log('WARNING: stdin ended, but keeping process alive');
  // Keep the process running forever
  setInterval(() => {}, 10000);
});

// Handle JSON-RPC messages
function handleMessage(message) {
  log(`Received message: ${message.method} (id: ${message.id})`);
  
  try {
    switch (message.method) {
      case 'initialize':
        sendResponse(message.id, {
          capabilities: {
            firecrawlProvider: {
              scrapeProvider: true,
              searchProvider: true,
              extractProvider: true
            }
          },
          serverInfo: {
            name: 'firecrawl-core',
            version: '1.0.0'
          }
        });
        break;
        
      case 'firecrawl/scrape':
        // Basic scraping response
        sendResponse(message.id, {
          url: message.params.url,
          content: `This is placeholder content for ${message.params.url}`,
          formats: message.params.formats || ['markdown'],
          timestamp: new Date().toISOString()
        });
        break;
        
      case 'firecrawl/search':
        // Basic search response
        sendResponse(message.id, {
          query: message.params.query,
          results: [
            {
              title: `Result for: ${message.params.query}`,
              url: `https://example.com/search?q=${encodeURIComponent(message.params.query)}`,
              description: 'This is a placeholder search result.'
            }
          ]
        });
        break;
        
      case 'shutdown':
        sendResponse(message.id, null);
        break;
        
      default:
        sendErrorResponse(message.id, -32601, `Method not supported: ${message.method}`);
    }
  } catch (err) {
    log(`Error handling message: ${err.message}`);
    sendErrorResponse(message.id, -32603, `Internal error: ${err.message}`);
  }
}

// Send a JSON-RPC response
function sendResponse(id, result) {
  const response = {
    jsonrpc: '2.0',
    id: id,
    result: result
  };
  
  log(`Sending response for id: ${id}`);
  process.stdout.write(JSON.stringify(response) + '\n');
}

// Send a JSON-RPC error response
function sendErrorResponse(id, code, message) {
  const response = {
    jsonrpc: '2.0',
    id: id,
    error: {
      code: code,
      message: message
    }
  };
  
  log(`Sending error response for id: ${id}: ${message}`);
  process.stdout.write(JSON.stringify(response) + '\n');
}

// This is critical: Keep the Node.js event loop active to prevent the process from exiting
setInterval(() => {
  log('Heartbeat: server still alive');
}, 30000);

log('Firecrawl MCP Server ready');
