#!/usr/bin/env node

/**
 * Firecrawl MCP Server Wrapper for Windows
 * 
 * This wrapper solves environment variable conflicts that affect the Firecrawl MCP server
 * on Windows platforms. It properly handles environment setup without breaking the JSON-RPC protocol.
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Set up environment for Firecrawl
process.env.FIRECRAWL_API_KEY = 'fc-54936f41b9894673bacd606878ce2d54';

// Prevent the ${APPDATA} variable error
const originalAppData = process.env.APPDATA;
process.env.APPDATA = '';

// Debug output to stderr (won't interfere with JSON-RPC)
console.error('Firecrawl MCP Wrapper: Starting server with fixed environment variables');

// Determine platform-specific commands
const isWindows = process.platform === 'win32';
const npmCmd = isWindows ? 'npm.cmd' : 'npm';

// Ensure firecrawl-mcp is installed
try {
  console.error('Checking if firecrawl-mcp is installed...');
  try {
    // Try to require the module to see if it's installed
    require.resolve('firecrawl-mcp');
    console.error('firecrawl-mcp is already installed');
  } catch (e) {
    // Module not found, install it
    console.error('Installing firecrawl-mcp...');
    execSync(`${npmCmd} install firecrawl-mcp --no-save`, { stdio: 'inherit' });
  }

  // Start the Firecrawl MCP server directly with Node.js
  console.error('Starting firecrawl-mcp...');
  
  // Find the actual path to the firecrawl-mcp executable
  let firecrawlPath;
  try {
    firecrawlPath = require.resolve('firecrawl-mcp/bin/firecrawl-mcp');
  } catch (e) {
    // Fallback to global module path
    const npmRoot = execSync(`${npmCmd} root -g`).toString().trim();
    firecrawlPath = path.join(npmRoot, 'firecrawl-mcp', 'bin', 'firecrawl-mcp');
    
    if (!fs.existsSync(firecrawlPath)) {
      // Last resort: try to find it in node_modules
      firecrawlPath = path.join(process.cwd(), 'node_modules', 'firecrawl-mcp', 'bin', 'firecrawl-mcp');
    }
  }
  
  console.error(`Found firecrawl-mcp at: ${firecrawlPath}`);
  
  // Run firecrawl-mcp directly with node
  const firecrawlProcess = spawn('node', [firecrawlPath], {
    stdio: 'inherit',
    env: process.env
  });

  // Handle clean shutdown
  firecrawlProcess.on('close', (code) => {
    console.error(`Firecrawl MCP Wrapper: Server exited with code ${code}`);
    process.env.APPDATA = originalAppData;
    process.exit(code);
  });

  // Forward signals
  process.on('SIGINT', () => firecrawlProcess.kill('SIGINT'));
  process.on('SIGTERM', () => firecrawlProcess.kill('SIGTERM'));
  
} catch (error) {
  console.error('Error in Firecrawl MCP wrapper:', error);
  process.env.APPDATA = originalAppData;
  process.exit(1);
}
