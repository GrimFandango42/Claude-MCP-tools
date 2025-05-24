#!/usr/bin/env node

/**
 * Windows Computer Use MCP Server - Node.js Implementation
 * This server provides Computer Use API functionality with strict protocol compliance
 */

const { spawn } = require('child_process');
const readline = require('readline');

// Set up readline interface for stdin
const rl = readline.createInterface({
  input: process.stdin,
  output: null,
  terminal: false
});

// Log to stderr only
function log(message) {
  console.error(`[windows-computer-use] ${message}`);
}

log('Starting Node.js Windows Computer Use MCP Server...');

// Take screenshot using PowerShell
async function takeScreenshot() {
  try {
    log('Taking screenshot...');
    
    // Use PowerShell to take screenshot
    const ps = spawn('powershell.exe', [
      '-Command',
      `
      Add-Type -AssemblyName System.Windows.Forms
      Add-Type -AssemblyName System.Drawing
      
      $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
      $bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
      $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
      $graphics.CopyFromScreen($screen.X, $screen.Y, 0, 0, $screen.Size)
      
      $tempFile = [System.IO.Path]::GetTempFileName() + '.png'
      $bitmap.Save($tempFile, [System.Drawing.Imaging.ImageFormat]::Png)
      
      $bytes = [System.IO.File]::ReadAllBytes($tempFile)
      $base64 = [Convert]::ToBase64String($bytes)
      
      Remove-Item $tempFile -Force
      
      Write-Output $base64
      Write-Output "$($screen.Width),$($screen.Height)"
      `
    ]);
    
    return new Promise((resolve, reject) => {
      let output = '';
      let error = '';
      
      ps.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      ps.stderr.on('data', (data) => {
        error += data.toString();
      });
      
      ps.on('close', (code) => {
        if (code !== 0) {
          reject(`PowerShell exited with code ${code}: ${error}`);
          return;
        }
        
        const lines = output.trim().split('\n');
        if (lines.length < 2) {
          reject('Invalid screenshot output');
          return;
        }
        
        const base64Image = lines[0];
        const dimensions = lines[1].split(',').map(Number);
        
        resolve({
          output: `Screenshot taken: ${dimensions[0]}x${dimensions[1]}`,
          image: base64Image,
          width: dimensions[0],
          height: dimensions[1]
        });
      });
    });
  } catch (error) {
    return { output: `ERROR: Screenshot failed: ${error.message || error}` };
  }
}

// Execute bash command in WSL
async function executeBash(command) {
  try {
    log(`Executing WSL command: ${command}`);
    
    const wsl = spawn('wsl', ['bash', '-c', command]);
    
    return new Promise((resolve, reject) => {
      let stdout = '';
      let stderr = '';
      
      wsl.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      wsl.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      wsl.on('error', (error) => {
        reject(`Failed to start WSL: ${error.message}`);
      });
      
      // Set timeout to prevent hanging
      const timeout = setTimeout(() => {
        wsl.kill();
        reject('Command timed out after 30 seconds');
      }, 30000);
      
      wsl.on('close', (code) => {
        clearTimeout(timeout);
        if (code === 0) {
          resolve({ output: stdout.trim() });
        } else {
          resolve({ output: `ERROR: ${stderr.trim()}\n${stdout.trim()}` });
        }
      });
    });
  } catch (error) {
    return { output: `ERROR: Failed to execute bash command: ${error.message || error}` };
  }
}

// Process incoming JSON-RPC requests
rl.on('line', async (line) => {
  try {
    const request = JSON.parse(line);
    const method = request.method || '';
    const id = request.id;
    
    log(`Received method: ${method} (id: ${id})`);
    
    let response;
    
    if (method === 'initialize') {
      response = {
        jsonrpc: '2.0',
        id,
        result: {
          protocolVersion: '2024-11-05',
          capabilities: { tools: {} },
          serverInfo: {
            name: 'windows-computer-use',
            version: '1.0.0'
          }
        }
      };
    }
    else if (method === 'tools/list') {
      response = {
        jsonrpc: '2.0',
        id,
        result: {
          tools: [
            {
              name: 'computer_20250124',
              description: 'Computer control',
              inputSchema: {
                type: 'object',
                properties: {
                  action: { type: 'string', enum: ['screenshot'] }
                },
                required: ['action']
              }
            },
            {
              name: 'bash_20250124',
              description: 'Execute bash',
              inputSchema: {
                type: 'object',
                properties: {
                  command: { type: 'string' }
                },
                required: ['command']
              }
            }
          ]
        }
      };
    }
    else if (method === 'resources/list') {
      response = {
        jsonrpc: '2.0',
        id,
        result: {
          resources: []
        }
      };
    }
    else if (method === 'prompts/list') {
      response = {
        jsonrpc: '2.0',
        id,
        result: {
          prompts: []
        }
      };
    }
    else if (method === 'tools/call') {
      const toolName = request.params.name;
      const args = request.params.arguments || {};
      
      let result;
      
      if (toolName === 'computer_20250124') {
        const action = args.action;
        
        if (action === 'screenshot') {
          result = await takeScreenshot();
        } else {
          result = { output: `ERROR: Unknown action: ${action}` };
        }
      }
      else if (toolName === 'bash_20250124') {
        const command = args.command;
        
        if (!command) {
          result = { output: 'ERROR: No command specified' };
        } else {
          result = await executeBash(command);
        }
      }
      else {
        result = { output: `ERROR: Unknown tool: ${toolName}` };
      }
      
      response = {
        jsonrpc: '2.0',
        id,
        result
      };
    }
    else {
      response = {
        jsonrpc: '2.0',
        id,
        error: {
          code: -32601,
          message: `Method not found: ${method}`
        }
      };
    }
    
    // Send response - strictly to stdout only
    console.log(JSON.stringify(response));
  }
  catch (error) {
    log(`ERROR: ${error.message || error}`);
    
    try {
      const errorResponse = {
        jsonrpc: '2.0',
        id: error.request?.id,
        error: {
          code: -32603,
          message: `Internal error: ${error.message || error}`
        }
      };
      
      console.log(JSON.stringify(errorResponse));
    } catch (e) {
      // Last resort error handling
    }
  }
});

// Keep the process running
process.on('SIGINT', () => {
  log('Received SIGINT, but keeping server alive');
});

process.on('SIGTERM', () => {
  log('Received SIGTERM, but keeping server alive');
});

// Handle any uncaught exceptions
process.on('uncaughtException', (error) => {
  log(`Uncaught exception: ${error.message}`);
  log(error.stack);
});

// Handle any unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  log(`Unhandled rejection at: ${promise}, reason: ${reason}`);
});