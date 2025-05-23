// firecrawl_direct.js - Robust Hybrid Firecrawl MCP Server
// Implements features from memory ed4e9254-7071-473c-9b82-ea1e8041279a
// Addresses common Node.js MCP server issues on Windows (memories 091237c3-bbb1-4ac0-ab86-84b40e5877e2, ba9c4eb0-ee6e-48f1-96ce-796d6f3d9333)

const readline = require('readline');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const SERVER_NAME = '[firecrawl-mcp-custom]';
const FIRECRAWL_API_KEY = process.env.FIRECRAWL_API_KEY || '';

function logError(...args) {
    console.error(SERVER_NAME, new Date().toISOString(), ...args);
}

function logInfo(...args) {
    console.error(SERVER_NAME, new Date().toISOString(), ...args);
}

function sendResponse(id, result) {
    const response = { jsonrpc: '2.0', id, result };
    process.stdout.write(JSON.stringify(response) + '\n');
}

function sendError(id, code, message, data = null) {
    const errorResponse = { jsonrpc: '2.0', id, error: { code, message, data } };
    process.stdout.write(JSON.stringify(errorResponse) + '\n');
}

let officialMCPServerProcess = null;
let useFallback = false;

async function initializeOfficialServer() {
    return new Promise((resolve) => {
        logInfo('Attempting to initialize official firecrawl-mcp server...');
        
        const npxArgs = ['-y', 'firecrawl-mcp@latest'];
        if (FIRECRAWL_API_KEY) {
            // The official server might pick up the API key from env, 
            // but we ensure it's explicitly passed if possible or handled by its own logic.
            // For now, relying on it picking up from process.env.FIRECRAWL_API_KEY
        }

        try {
            officialMCPServerProcess = spawn('npx', npxArgs, {
                stdio: ['pipe', 'pipe', 'pipe'], // pipe stdin, stdout, stderr
                env: { ...process.env, FIRECRAWL_API_KEY }, // Ensure API key is in the child's environment
                shell: process.platform === 'win32' // Use shell on Windows for npx
            });

            officialMCPServerProcess.stdout.on('data', (data) => {
                // Forward stdout from official server to our stdout
                process.stdout.write(data);
            });

            officialMCPServerProcess.stderr.on('data', (data) => {
                logError('Official Server STDERR:', data.toString().trim());
            });

            officialMCPServerProcess.on('error', (err) => {
                logError('Failed to start official firecrawl-mcp process:', err.message);
                useFallback = true;
                resolve(false); // Indicate failure
            });

            officialMCPServerProcess.on('exit', (code, signal) => {
                logInfo(`Official server process exited with code ${code}, signal ${signal}`);
                // If it exits too soon after an initialize attempt, it might be problematic.
                // For now, we'll assume if it starts and then exits, it's an issue.
                if (!useFallback) { // if not already switched to fallback
                    useFallback = true; 
                    logInfo('Official server exited unexpectedly. Switching to fallback mode if not already done.');
                }
            });
            
            // A simple check: if the process is running, assume it's okay for now.
            // More robust checks would involve handshake, but this is a wrapper.
            if (officialMCPServerProcess.pid) {
                logInfo('Official firecrawl-mcp process started successfully. PID:', officialMCPServerProcess.pid);
                resolve(true); // Indicate success
            } else {
                logError('Official firecrawl-mcp process did not start.');
                useFallback = true;
                resolve(false);
            }

        } catch (error) {
            logError('Exception during official server spawn:', error.message);
            useFallback = true;
            resolve(false);
        }
    });
}

// Fallback mode tools (minimal implementation)
async function fallbackScrape(params) {
    logInfo('Using fallback scrape tool.');
    if (!FIRECRAWL_API_KEY) {
        return { error: 'API key not configured for fallback mode.' };
    }
    if (!params || !params.url) {
        return { error: 'URL parameter is required for fallback scrape.' };
    }
    // This is a placeholder. A real fallback would use a basic HTTP GET.
    // For now, it demonstrates the structure.
    try {
        // const response = await fetch(params.url); // Requires node-fetch or similar
        // const text = await response.text();
        // return { content: text.substring(0, 500) + '...' }; // Example
        return { data: { content: `Fallback scrape for ${params.url} (API key: ${FIRECRAWL_API_KEY ? 'present' : 'missing'}) - actual fetch not implemented in this placeholder.`}};
    } catch (e) {
        logError('Fallback scrape error:', e.message);
        return { error: e.message };
    }
}

async function fallbackSearch(params) {
    logInfo('Using fallback search tool.');
    return { results: 'Fallback search not implemented.' };
}

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

rl.on('line', async (line) => {
    try {
        const request = JSON.parse(line);
        logInfo('Received request:', JSON.stringify(request));

        if (request.method === 'initialize') {
            const officialServerOk = await initializeOfficialServer();
            if (officialServerOk && !useFallback) {
                // If official server is up, forward the initialize request
                officialMCPServerProcess.stdin.write(line + '\n');
            } else {
                // Fallback initialize
                logInfo('Initializing in fallback mode.');
                sendResponse(request.id, {
                    name: 'firecrawl-mcp-custom (fallback)',
                    version: '0.1.0',
                    tools: [
                        {
                            name: 'scrape',
                            description: 'Fallback: Scrapes a URL (basic).',
                            input_schema: { type: 'object', properties: { url: { type: 'string' } } }
                        },
                        {
                            name: 'search',
                            description: 'Fallback: Performs a search (not implemented).',
                            input_schema: { type: 'object', properties: { query: { type: 'string' } } }
                        }
                    ]
                });
            }
            return;
        }

        if (useFallback || !officialMCPServerProcess || !officialMCPServerProcess.stdin.writable) {
            logInfo('Processing with fallback tool:', request.method);
            let result;
            if (request.method === 'scrape') {
                result = await fallbackScrape(request.params);
            } else if (request.method === 'search') {
                result = await fallbackSearch(request.params);
            } else {
                sendError(request.id, -32601, 'Method not found in fallback mode');
                return;
            }
            if (result.error) {
                sendError(request.id, -32000, result.error);
            } else {
                sendResponse(request.id, result);
            }
        } else {
            // Forward to official server
            logInfo('Forwarding to official server:', request.method);
            officialMCPServerProcess.stdin.write(line + '\n');
        }
    } catch (error) {
        logError('Error processing line:', line, error.message, error.stack);
        sendError(null, -32700, 'Parse error or internal server error');
    }
});

// Keepalive and stream handling
process.stdin.resume(); // Keep stdin open
process.on('SIGINT', () => {
    logInfo('Received SIGINT. Exiting gracefully.');
    if (officialMCPServerProcess) officialMCPServerProcess.kill('SIGINT');
    process.exit(0);
});
process.on('SIGTERM', () => {
    logInfo('Received SIGTERM. Exiting gracefully.');
    if (officialMCPServerProcess) officialMCPServerProcess.kill('SIGTERM');
    process.exit(0);
});

logInfo('Custom Firecrawl MCP Server (hybrid) started. Listening on stdin.');
logInfo(`FIRECRAWL_API_KEY is ${FIRECRAWL_API_KEY ? 'set' : 'not set'}.`);

// Handle the case where stdin closes unexpectedly
process.stdin.on('end', () => {
    logInfo('Stdin stream ended. Exiting.');
    if (officialMCPServerProcess) officialMCPServerProcess.kill();
    process.exit(0);
});

process.on('uncaughtException', (err) => {
  logError('Uncaught Exception:', err.message, err.stack);
  // Decide if to exit or try to recover, for now, exit
  if (officialMCPServerProcess) officialMCPServerProcess.kill();
  process.exit(1);
});
