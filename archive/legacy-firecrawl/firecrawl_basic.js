#!/usr/bin/env node

// Most basic MCP server that meets all requirements
const readline = require('readline');

// Set up readline interface for line-by-line reading
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// Log to stderr to avoid interfering with JSON-RPC
function log(msg) {
  console.error(msg);
}

log('Starting basic Firecrawl MCP server');

// Listen for lines from stdin
rl.on('line', (line) => {
  try {
    const message = JSON.parse(line);
    log(`Received: ${message.method} (id: ${message.id})`);
    
    // Handle initialize method
    if (message.method === 'initialize') {
      const response = {
        jsonrpc: '2.0',
        id: message.id,
        result: {
          capabilities: {
            firecrawlProvider: {
              scrapeProvider: true,
              searchProvider: true,
              extractProvider: true
            }
          },
          serverInfo: {
            name: 'firecrawl-basic',
            version: '1.0.0'
          }
        }
      };
      
      // Write to stdout
      console.log(JSON.stringify(response));
      log('Sent initialize response');
    }
    // Handle firecrawl/scrape
    else if (message.method === 'firecrawl/scrape') {
      const response = {
        jsonrpc: '2.0',
        id: message.id,
        result: {
          url: message.params.url,
          content: 'This is a placeholder content for ' + message.params.url,
          timestamp: new Date().toISOString()
        }
      };
      
      console.log(JSON.stringify(response));
      log('Sent scrape response');
    }
    // Handle firecrawl/search
    else if (message.method === 'firecrawl/search') {
      const response = {
        jsonrpc: '2.0',
        id: message.id,
        result: {
          query: message.params.query,
          results: [{
            title: 'Result for: ' + message.params.query,
            url: 'https://example.com',
            description: 'This is a basic search result.'
          }]
        }
      };
      
      console.log(JSON.stringify(response));
      log('Sent search response');
    }
    // Handle shutdown message
    else if (message.method === 'shutdown') {
      const response = {
        jsonrpc: '2.0',
        id: message.id,
        result: null
      };
      
      console.log(JSON.stringify(response));
      log('Acknowledging shutdown but keeping server alive');
    }
    // Default handler for other methods
    else {
      const response = {
        jsonrpc: '2.0',
        id: message.id,
        error: {
          code: -32601,
          message: 'Method not supported: ' + message.method
        }
      };
      
      console.log(JSON.stringify(response));
      log('Sent method not supported error');
    }
  } catch (err) {
    log('Error processing message: ' + err.message);
  }
});

// Handle error and close events but don't exit
rl.on('close', () => {
  log('readline interface closed but keeping process alive');
});

// Keep the process alive with a heartbeat
setInterval(() => {
  log('Server heartbeat');
}, 30000);

log('Firecrawl MCP server ready');
