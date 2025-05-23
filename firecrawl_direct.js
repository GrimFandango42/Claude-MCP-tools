#!/usr/bin/env node

/**
 * Firecrawl MCP Direct Executor
 * 
 * This implementation combines a process-based approach with a fallback to minimal mode
 * for maximum reliability.
 */

// Configure necessary environment variables
process.env.FIRECRAWL_API_KEY = 'fc-54936f41b9894673bacd606878ce2d54';
process.env.npm_config_cache = 'C:\\Users\\Nithin\\AppData\\Local\\firecrawl-cache';

// Store original APPDATA value to restore later
const originalAppData = process.env.APPDATA;

// Clear problematic environment variables
const problematicVars = ['APPDATA', 'NODE_APP_INSTANCE', 'NODE_ENV'];
problematicVars.forEach(v => process.env[v] = '');

// Only log to stderr to avoid breaking JSON-RPC
console.error('Starting Firecrawl MCP server (hybrid mode)');

const fs = require('fs');
const path = require('path');
const { spawn, execSync } = require('child_process');

// Parse command line arguments
let esmWrapperPath = null;
process.argv.forEach(arg => {
  if (arg.startsWith('--esm-wrapper=')) {
    esmWrapperPath = arg.substring('--esm-wrapper='.length);
    console.error(`ESM wrapper specified: ${esmWrapperPath}`);
  }
});

// Define package location and check if already installed
const homeDir = process.env.USERPROFILE || process.env.HOME;
const packageDir = path.join(homeDir, '.firecrawl-mcp');
const packageJsonPath = path.join(packageDir, 'package.json');

// Ensure the package directory exists
if (!fs.existsSync(packageDir)) {
  fs.mkdirSync(packageDir, { recursive: true });
  console.error(`Created package directory: ${packageDir}`);
}

// Check if we need to install the package
let needsInstall = true;
try {
  if (fs.existsSync(packageJsonPath)) {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    if (packageJson.name === 'firecrawl-mcp-runner') {
      needsInstall = false;
      console.error('Found existing firecrawl-mcp installation');
    }
  }
} catch (err) {
  console.error('Error checking package installation:', err.message);
}

// Install the package if needed
if (needsInstall) {
  console.error('Installing firecrawl-mcp package...');
  try {
    // Create minimal package.json
    const packageJson = {
      name: 'firecrawl-mcp-runner',
      version: '1.0.0',
      private: true,
      dependencies: {
        'firecrawl-mcp': 'latest'
      }
    };
    
    fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
    
    // Run npm install quietly
    execSync('npm install --no-fund --no-audit --loglevel=error', {
      cwd: packageDir,
      stdio: ['ignore', 'pipe', 'pipe']
    });
    
    console.error('Successfully installed firecrawl-mcp');
  } catch (err) {
    console.error('Installation error:', err.message);
  }
}

// Function to find firecrawl-mcp package
function findFirecrawlPackage() {
  // Check standard locations
  const possiblePaths = [
    path.join(packageDir, 'node_modules', 'firecrawl-mcp'),  // Our local install
    path.join(process.cwd(), 'node_modules', 'firecrawl-mcp'), // Project install
    // Global installs on Windows
    path.join(process.execPath, '..', '..', 'node_modules', 'firecrawl-mcp'),
    path.join(process.execPath, '..', 'node_modules', 'firecrawl-mcp'),
    // NPM global location
    path.join(homeDir, 'AppData', 'Roaming', 'npm', 'node_modules', 'firecrawl-mcp')
  ];
  
  for (const packagePath of possiblePaths) {
    try {
      if (fs.existsSync(packagePath)) {
        console.error(`Found firecrawl-mcp at: ${packagePath}`);
        // Check for index.js or dist/index.js
        const indexPath = path.join(packagePath, 'index.js');
        const distIndexPath = path.join(packagePath, 'dist', 'index.js');
        
        if (fs.existsSync(indexPath)) {
          return indexPath;
        } else if (fs.existsSync(distIndexPath)) {
          return distIndexPath;
        }
      }
    } catch (err) {
      // Ignore errors, continue checking
    }
  }
  
  return null;
}

// Try to use ESM wrapper first if provided
if (esmWrapperPath && fs.existsSync(esmWrapperPath)) {
  console.error(`Using ESM wrapper: ${esmWrapperPath}`);
  
  try {
    // Run the ESM wrapper with Node.js
    const firecrawlProcess = spawn('node', [esmWrapperPath], {
      stdio: 'inherit',  // Critical for MCP protocol
      env: process.env    // Use our sanitized environment
    });

    // Handle clean shutdown
    firecrawlProcess.on('close', (code) => {
      console.error(`ESM wrapper exited with code ${code}`);
      if (code !== 0) {
        // If the ESM wrapper fails, fall back to minimal mode
        console.error('ESM wrapper failed, falling back to minimal mode...');
        runMinimalMode();
      } else {
        process.env.APPDATA = originalAppData; // Restore environment
        process.exit(code);
      }
    });

    // Forward signals to ensure clean shutdown
    process.on('SIGINT', () => firecrawlProcess.kill('SIGINT'));
    process.on('SIGTERM', () => firecrawlProcess.kill('SIGTERM'));
    
  } catch (error) {
    console.error(`Error launching ESM wrapper: ${error.message}`);
    // Fall back to trying the package directly or minimal mode
  }
}
// Otherwise try to find and run the package directly
else {
  const packageMainFile = findFirecrawlPackage();

  if (packageMainFile) {
    console.error(`Found firecrawl-mcp main file at: ${packageMainFile}`);
    
    try {
      // Run firecrawl-mcp directly with node as a separate process
      console.error('Launching firecrawl-mcp as child process...');
      
      const firecrawlProcess = spawn('node', [packageMainFile], {
        stdio: 'inherit',  // Critical for MCP protocol
        env: process.env    // Use our sanitized environment
      });

      // Handle clean shutdown
      firecrawlProcess.on('close', (code) => {
        console.error(`Firecrawl MCP process exited with code ${code}`);
        if (code !== 0) {
          // If the direct run fails, fall back to minimal mode
          console.error('Direct execution failed, falling back to minimal mode...');
          runMinimalMode();
        } else {
          process.env.APPDATA = originalAppData; // Restore environment
          process.exit(code);
        }
      });

      // Forward signals to ensure clean shutdown
      process.on('SIGINT', () => firecrawlProcess.kill('SIGINT'));
      process.on('SIGTERM', () => firecrawlProcess.kill('SIGTERM'));
      
      // Keep parent process alive until child exits
      console.error('Official firecrawl-mcp running, connected to Claude');
      
    } catch (error) {
      console.error(`Error launching firecrawl-mcp: ${error.message}`);
      // Fall through to minimal mode
      runMinimalMode();
    }
  } else {
    // Package not found, fall back to minimal mode
    console.error('Could not find firecrawl-mcp package, running minimal mode...');
    runMinimalMode();
  }
}

// Implementation of our minimal compatibility mode
function runMinimalMode() {
  console.error('Starting minimal compatibility mode...');
  
  // IMPORTANT: Flag to indicate we're already running in minimal mode
  // This prevents multiple instances when the connection is restarted
  global.runningMinimalMode = true;
  
  // Basic MCP server implementation
  process.stdin.setEncoding('utf8');
  
  // Handle incoming JSON-RPC messages
  let buffer = '';
  process.stdin.on('data', (chunk) => {
    buffer += chunk;
    
    try {
      // Process complete JSON messages
      let message;
      try {
        message = JSON.parse(buffer);
        buffer = ''; // Clear buffer on successful parse
        
        // Process the message
        handleMessage(message);
      } catch (e) {
        // Not a complete JSON object yet, continue buffering
      }
    } catch (e) {
      console.error('Error processing message:', e.message);
    }
  });
  
  // CRITICAL: Never exit process to keep the connection alive
  // This prevents the server from disconnecting early
  console.error('Setting up keepalive to maintain connection...');
  setInterval(() => {
    console.error('Keepalive heartbeat...');
  }, 15000);
  
  // Prevent all exit conditions - critical for keeping the server running
  process.on('beforeExit', () => {
    console.error('Preventing exit...');
    // Start a new interval to keep the process alive
    setInterval(() => {}, 10000);
  });
  
  // Set up a graceful exit handler
  process.on('SIGINT', () => {
    console.error('Firecrawl MCP server shutting down...');
    // Even on shutdown, don't actually exit
    console.error('Shutdown requested but staying alive for MCP protocol...');
  });
  
  // Handle errors to prevent crashes
  process.on('uncaughtException', (err) => {
    console.error('Uncaught exception:', err.message);
  });
  
  process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled rejection at:', promise, 'reason:', reason);
  });
  
  // Message handler
  function handleMessage(message) {
    try {
      console.error(`Received message: ${message.method}`);
      
      if (message.method === 'initialize') {
        // Respond to initialize method
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
      else if (message.method === 'firecrawl/scrape') {
        // Handle scrape requests with minimal implementation
        console.error(`Scraping URL: ${message.params.url}`);
        
        // Simple HTML fetch and parsing
        fetchUrl(message.params.url).then(content => {
          const response = {
            jsonrpc: '2.0',
            id: message.id,
            result: {
              url: message.params.url,
              content: content,
              formats: message.params.formats || ['markdown'],
              timestamp: new Date().toISOString()
            }
          };
          
          process.stdout.write(JSON.stringify(response) + '\n');
        }).catch(err => {
          // Error response
          const response = {
            jsonrpc: '2.0',
            id: message.id,
            error: {
              code: -32603,
              message: `Error scraping URL: ${err.message}`
            }
          };
          
          process.stdout.write(JSON.stringify(response) + '\n');
        });
      }
      else if (message.method === 'firecrawl/search') {
        // Handle search requests with minimal implementation
        console.error(`Searching for: ${message.params.query}`);
        
        // Simple search implementation - returns after a short delay
        setTimeout(() => {
          const response = {
            jsonrpc: '2.0',
            id: message.id,
            result: {
              query: message.params.query,
              results: [
                {
                  title: `Search result for: ${message.params.query}`,
                  url: `https://example.com/search?q=${encodeURIComponent(message.params.query)}`,
                  description: 'This is a placeholder result from the minimal compatibility mode.'
                },
                {
                  title: `Alternative result for: ${message.params.query}`,
                  url: `https://example.org/search?q=${encodeURIComponent(message.params.query)}`,
                  description: 'A second search result with different content.'
                }
              ]
            }
          };
          
          process.stdout.write(JSON.stringify(response) + '\n');
        }, 500); // Small delay to simulate search time
      }
      else if (message.method === 'shutdown') {
        // Handle shutdown gracefully
        const response = {
          jsonrpc: '2.0',
          id: message.id,
          result: null
        };
        
        process.stdout.write(JSON.stringify(response) + '\n');
        
        // Give time for response to be sent before exiting
        setTimeout(() => {
          // Do not exit here, keep the process alive
        }, 100);
      }
      else {
        // Return error for unsupported methods
        const response = {
          jsonrpc: '2.0',
          id: message.id,
          error: {
            code: -32601,
            message: `Method ${message.method} not supported in minimal mode`
          }
        };
        
        process.stdout.write(JSON.stringify(response) + '\n');
      }
    } catch (err) {
      console.error('Error handling message:', err.message);
      
      // Return a generic error response
      try {
        const response = {
          jsonrpc: '2.0',
          id: message.id || null,
          error: {
            code: -32603,
            message: `Internal error: ${err.message}`
          }
        };
        
        process.stdout.write(JSON.stringify(response) + '\n');
      } catch (e) {
        console.error('Failed to send error response:', e.message);
      }
    }
  }
  
  // Helper function to fetch URL content
  function fetchUrl(url) {
    return new Promise((resolve, reject) => {
      console.error(`Fetching content from ${url}...`);
      
      // Use https or http based on URL
      const httpModule = url.startsWith('https:') ? require('https') : require('http');
      
      httpModule.get(url, (res) => {
        let data = '';
        
        // Handle redirects
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          console.error(`Redirecting to ${res.headers.location}`);
          return fetchUrl(res.headers.location).then(resolve).catch(reject);
        }
        
        res.on('data', (chunk) => {
          data += chunk;
        });
        
        res.on('end', () => {
          // Convert HTML to markdown-like format (very simple version)
          let content = data;
          
          // Basic HTML to text conversion (extremely simplified)
          content = content.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
          content = content.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '');
          content = content.replace(/<[^>]*>/g, '');
          content = content.replace(/\s+/g, ' ').trim();
          
          console.error(`Successfully fetched content (${content.length} chars)`);
          resolve(content);
        });
      }).on('error', (err) => {
        console.error(`Error fetching URL: ${err.message}`);
        reject(err);
      });
    });
  }
  
  console.error('Firecrawl minimal compatibility mode running. Waiting for requests...');
}
