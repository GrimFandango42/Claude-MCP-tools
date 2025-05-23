/**
 * MCP Service Manager for Firecrawl
 * Ensures stable connection with proper process lifecycle management
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configure logging to a file for debugging
const logFile = fs.createWriteStream(path.join(__dirname, 'mcp_service.log'), { flags: 'a' });

function log(message) {
  const timestamp = new Date().toISOString();
  const entry = `[${timestamp}] ${message}\n`;
  
  // Write to log file
  logFile.write(entry);
  
  // Also to stderr (for Claude Desktop logs)
  process.stderr.write(entry);
}

log('MCP Service Manager starting');

// Environment setup
const env = {
  ...process.env,
  FIRECRAWL_API_KEY: 'fc-54936f41b9894673bacd606878ce2d54',
  NODE_ENV: 'production'
};

// Delete problematic environment variables
delete env.APPDATA;

// Function to start the child process
function startMcpServer() {
  log('Spawning MCP server process');
  
  // Spawn the server process
  const serverProcess = spawn('node', 
    [path.join(__dirname, 'firecrawl_optimized.js')], 
    {
      env,
      stdio: ['pipe', 'pipe', 'pipe'] // [stdin, stdout, stderr]
    }
  );
  
  // Connect parent process stdin → child process stdin
  process.stdin.pipe(serverProcess.stdin);
  
  // Connect child process stdout → parent process stdout
  serverProcess.stdout.pipe(process.stdout);
  
  // Log stderr output but don't forward it
  serverProcess.stderr.on('data', (data) => {
    log(`Server stderr: ${data.toString().trim()}`);
  });
  
  // Handle process exit
  serverProcess.on('exit', (code, signal) => {
    log(`Server process exited with code ${code} and signal ${signal}`);
    log('Restarting server...');
    
    // Restart after a short delay
    setTimeout(startMcpServer, 1000);
  });
  
  // Handle process errors
  serverProcess.on('error', (err) => {
    log(`Server process error: ${err.message}`);
  });
  
  return serverProcess;
}

// Start the server
let serverProcess = startMcpServer();

// Handle signals but don't exit
process.on('SIGINT', () => {
  log('Received SIGINT but ignoring it');
});

process.on('SIGTERM', () => {
  log('Received SIGTERM but ignoring it');
});

// Keep the main process alive
process.stdin.resume();

log('MCP Service Manager ready');
