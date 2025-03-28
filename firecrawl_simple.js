#!/usr/bin/env node

/**
 * Ultra-Minimal Firecrawl MCP Server
 * Designed for maximum compatibility and connection stability
 */

// Log to stderr only
function log(msg) {
  process.stderr.write(msg + '\n');
}

log('Starting Ultra-Minimal Firecrawl MCP Server');

// Keep the process alive
setInterval(() => {}, 10000);

// Handle JSON-RPC messages
process.stdin.on('data', (chunk) => {
  try {
    const message = JSON.parse(chunk);
    
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
            name: 'firecrawl-minimal',
            version: '1.0.0'
          }
        }
      };
      
      process.stdout.write(JSON.stringify(response) + '\n');
    }
    // Handle other methods with minimal responses
    else if (message.method === 'firecrawl/scrape') {
      const response = {
        jsonrpc: '2.0',
        id: message.id,
        result: {
          url: message.params.url,
          content: 'Content could not be retrieved in minimal mode',
          formats: ['markdown'],
          timestamp: new Date().toISOString()
        }
      };
      
      process.stdout.write(JSON.stringify(response) + '\n');
    }
    else if (message.method === 'firecrawl/search') {
      const response = {
        jsonrpc: '2.0',
        id: message.id,
        result: {
          query: message.params.query,
          results: [{
            title: 'Minimal mode result',
            url: 'https://example.com',
            description: 'Minimal mode does not support real search'
          }]
        }
      };
      
      process.stdout.write(JSON.stringify(response) + '\n');
    }
    else {
      // Default response for other methods
      const response = {
        jsonrpc: '2.0',
        id: message.id,
        result: null
      };
      
      process.stdout.write(JSON.stringify(response) + '\n');
    }
  } catch (error) {
    // Ignore parsing errors
  }
});

// Prevent crashes
process.on('uncaughtException', () => {});
process.on('unhandledRejection', () => {});

log('Ultra-Minimal Firecrawl MCP Server ready');
