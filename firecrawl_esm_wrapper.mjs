#!/usr/bin/env node

/**
 * ESM Wrapper for Firecrawl MCP
 * 
 * This file is an ESM module (.mjs extension) that properly imports
 * and executes the Firecrawl MCP ES module package.
 */

// Configure environment variables
process.env.FIRECRAWL_API_KEY = 'fc-54936f41b9894673bacd606878ce2d54';
process.env.npm_config_cache = 'C:\\Users\\Nithin\\AppData\\Local\\firecrawl-cache';

// Clear problematic environment variables
const problematicVars = ['APPDATA', 'NODE_APP_INSTANCE', 'NODE_ENV'];
problematicVars.forEach(v => process.env[v] = '');

// Log to stderr only to maintain JSON-RPC protocol
console.error('Starting Firecrawl MCP server (ESM mode)');

// Find the package path
const fs = await import('fs');
const path = await import('path');

// Define possible package locations
const homeDir = process.env.USERPROFILE || process.env.HOME;
const packageLocations = [
  // Local install in user's home directory
  path.join(homeDir, '.firecrawl-mcp', 'node_modules', 'firecrawl-mcp'),
  // Project-level install
  path.join(process.cwd(), 'node_modules', 'firecrawl-mcp'),
  // Global installs
  path.join(process.execPath, '..', '..', 'node_modules', 'firecrawl-mcp'),
  path.join(homeDir, 'AppData', 'Roaming', 'npm', 'node_modules', 'firecrawl-mcp')
];

// Find the first valid location
let packagePath = null;
for (const location of packageLocations) {
  try {
    if (fs.existsSync(location)) {
      packagePath = location;
      console.error(`Found firecrawl-mcp at: ${packagePath}`);
      break;
    }
  } catch (err) {
    // Ignore errors, try next location
  }
}

// Dynamic import of the Firecrawl MCP package
if (packagePath) {
  try {
    // Try to import the file that implements the MCP server
    console.error(`Importing package from ${packagePath}...`);
    
    // Use file: protocol to import from local filesystem
    const packageUrl = `file://${packagePath.replace(/\\/g, '/')}/dist/index.js`;
    console.error(`Import URL: ${packageUrl}`);
    
    // Import the module
    await import(packageUrl);
  } catch (err) {
    console.error(`Failed to import package: ${err.message}`);
    process.exit(1); // Exit with error code so direct.js can fall back to minimal mode
  }
} else {
  console.error('Could not find firecrawl-mcp package');
  process.exit(1);
}
