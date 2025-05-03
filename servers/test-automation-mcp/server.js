#!/usr/bin/env node
/**
 * Test Automation MCP Server
 * 
 * A Model Context Protocol server that provides end-to-end test automation
 * capabilities using Playwright, Puppeteer, and WinAppDriver.
 * 
 * JSONRPC communication happens over stdin/stdout, with logs going to stderr.
 */

// --- Core dependencies ---
const { spawn, fork } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');

// --- Simple structured logging to stderr ---
function log(level, message, meta = {}) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    ...meta
  };
  console.error(JSON.stringify(logEntry));
}

const logger = {
  info: (message, meta) => log('info', message, meta),
  error: (message, meta) => log('error', message, meta),
  warn: (message, meta) => log('warn', message, meta),
  debug: (message, meta) => log('debug', message, meta)
};

// --- Path Configuration ---
const ARTIFACT_DIR = process.env.TEST_AUTOMATION_ARTIFACTS_DIR || 
  path.join(os.homedir(), '.test-automation-mcp', 'artifacts');

// Ensure artifact directory exists
if (!fs.existsSync(ARTIFACT_DIR)) {
  try {
    fs.mkdirSync(ARTIFACT_DIR, { recursive: true });
    logger.info(`Created artifact directory: ${ARTIFACT_DIR}`);
  } catch (err) {
    logger.error(`Failed to create artifact directory: ${err.message}`);
  }
}

// --- Playwright Helpers ---
let browserContext = null;
let page = null;

async function ensurePlaywright() {
  try {
    return require('@playwright/test');
  } catch (err) {
    logger.error(`Failed to load Playwright: ${err.message}`);
    throw new Error('Playwright not available. Please install with: npx playwright install');
  }
}

// --- MCP Server Setup ---
class SimpleMcpServer {
  constructor(name) {
    this.name = name;
    this.tools = new Map();
    this.initialized = false;
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    this.rl.on('line', this.handleLine.bind(this));
  }

  async handleLine(line) {
    try {
      const request = JSON.parse(line);
      if (!request.id || !request.method) {
        this.sendErrorResponse(request.id || 0, -32600, 'Invalid request');
        return;
      }

      if (request.method === 'initialize') {
        this.sendResponse(request.id, {
          name: this.name,
          version: '0.1.0',
          capabilities: {
            tools: Array.from(this.tools.keys()).map(name => ({
              name,
              description: this.tools.get(name).description || ''
            }))
          }
        });
        this.initialized = true;
        return;
      }

      if (request.method === 'shutdown') {
        this.sendResponse(request.id, { success: true });
        return;
      }

      if (!this.initialized && request.method !== 'initialize') {
        this.sendErrorResponse(request.id, -32002, 'Server not initialized');
        return;
      }

      const tool = this.tools.get(request.method);
      if (!tool) {
        this.sendErrorResponse(request.id, -32601, `Method ${request.method} not found`);
        return;
      }

      try {
        const result = await tool.handler(request.params || {});
        this.sendResponse(request.id, result);
      } catch (err) {
        logger.error(`Error executing tool ${request.method}:`, { error: err.message, stack: err.stack });
        this.sendErrorResponse(request.id, -32000, err.message);
      }
    } catch (err) {
      logger.error('Error parsing request:', { error: err.message, stack: err.stack });
      this.sendErrorResponse(0, -32700, 'Parse error');
    }
  }

  sendResponse(id, result) {
    const response = {
      jsonrpc: '2.0',
      id,
      result
    };
    console.log(JSON.stringify(response));
  }

  sendErrorResponse(id, code, message) {
    const response = {
      jsonrpc: '2.0',
      id,
      error: {
        code,
        message
      }
    };
    console.log(JSON.stringify(response));
  }

  addTool(name, description, handler) {
    this.tools.set(name, { description, handler });
    logger.info(`Registered tool: ${name}`);
  }
}

const server = new SimpleMcpServer('test-automation-mcp');

// --- Register Tools ---

// Browser Management
server.addTool('launch_browser', 'Launch a browser instance', async ({ browserType = 'chromium', headless = true }) => {
  try {
    logger.info(`Launching browser: ${browserType}`);
    const playwright = await ensurePlaywright();
    
    const browser = await playwright[browserType].launch({ headless });
    browserContext = await browser.newContext();
    page = await browserContext.newPage();
    
    return { success: true, message: `Launched ${browserType} browser` };
  } catch (err) {
    logger.error(`Failed to launch browser: ${err.message}`);
    return { success: false, error: err.message };
  }
});

server.addTool('close_browser', 'Close the active browser', async () => {
  try {
    if (page) {
      await page.close();
      page = null;
    }
    if (browserContext) {
      await browserContext.close();
      browserContext = null;
    }
    return { success: true, message: 'Browser closed' };
  } catch (err) {
    logger.error(`Failed to close browser: ${err.message}`);
    return { success: false, error: err.message };
  }
});

server.addTool('list_browsers', 'List available browser engines', async () => {
  try {
    return {
      available: ['chromium', 'firefox', 'webkit'],
      recommended: 'chromium'
    };
  } catch (err) {
    logger.error(`Failed to list browsers: ${err.message}`);
    return { success: false, error: err.message };
  }
});

// Navigation
server.addTool('goto', 'Navigate to a URL', async ({ url }) => {
  try {
    if (!page) {
      throw new Error('No active browser page. Call launch_browser first.');
    }
    
    logger.info(`Navigating to: ${url}`);
    const response = await page.goto(url, { waitUntil: 'networkidle' });
    
    return { 
      success: true, 
      status: response.status(),
      url: page.url()
    };
  } catch (err) {
    logger.error(`Failed to navigate: ${err.message}`);
    return { success: false, error: err.message };
  }
});

// Interaction
server.addTool('click', 'Click an element on the page', async ({ selector }) => {
  try {
    if (!page) {
      throw new Error('No active browser page. Call launch_browser first.');
    }
    
    logger.info(`Clicking element: ${selector}`);
    await page.click(selector);
    
    return { success: true };
  } catch (err) {
    logger.error(`Failed to click element: ${err.message}`);
    return { success: false, error: err.message };
  }
});

server.addTool('fill', 'Fill a form field with text', async ({ selector, value }) => {
  try {
    if (!page) {
      throw new Error('No active browser page. Call launch_browser first.');
    }
    
    logger.info(`Filling form field: ${selector}`);
    await page.fill(selector, value);
    
    return { success: true };
  } catch (err) {
    logger.error(`Failed to fill form field: ${err.message}`);
    return { success: false, error: err.message };
  }
});

// Assertions
server.addTool('assert_element', 'Assert the state of an element', async ({ selector, state = 'visible', timeout = 5000 }) => {
  try {
    if (!page) {
      throw new Error('No active browser page. Call launch_browser first.');
    }
    
    logger.info(`Asserting element: ${selector} is ${state}`);
    
    let result = false;
    switch (state) {
      case 'visible':
        await page.waitForSelector(selector, { state: 'visible', timeout });
        result = true;
        break;
      case 'hidden':
        await page.waitForSelector(selector, { state: 'hidden', timeout });
        result = true;
        break;
      case 'enabled':
        await page.waitForSelector(selector, { state: 'visible', timeout });
        const isDisabled = await page.$eval(selector, el => el.hasAttribute('disabled'));
        result = !isDisabled;
        break;
      default:
        throw new Error(`Unknown state: ${state}`);
    }
    
    return { 
      success: true, 
      result: result,
      message: `Element ${selector} is ${state}: ${result}`
    };
  } catch (err) {
    logger.error(`Assertion failed for element: ${err.message}`);
    return { 
      success: false, 
      result: false,
      error: err.message 
    };
  }
});

// Artifacts
server.addTool('capture_screenshot', 'Capture a screenshot of the page or element', async ({ selector, path: screenshotPath }) => {
  try {
    if (!page) {
      throw new Error('No active browser page. Call launch_browser first.');
    }
    
    // Generate a filename if not provided
    if (!screenshotPath) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      screenshotPath = path.join(ARTIFACT_DIR, `screenshot-${timestamp}.png`);
    } else if (!path.isAbsolute(screenshotPath)) {
      screenshotPath = path.join(ARTIFACT_DIR, screenshotPath);
    }
    
    logger.info(`Capturing screenshot to: ${screenshotPath}`);
    
    if (selector) {
      const element = await page.$(selector);
      if (!element) {
        throw new Error(`Element not found: ${selector}`);
      }
      await element.screenshot({ path: screenshotPath });
    } else {
      await page.screenshot({ path: screenshotPath, fullPage: true });
    }
    
    return { 
      success: true, 
      path: screenshotPath
    };
  } catch (err) {
    logger.error(`Failed to capture screenshot: ${err.message}`);
    return { success: false, error: err.message };
  }
});

// Test steps and suites
server.addTool('run_steps', 'Run a sequence of test steps', async ({ steps }) => {
  try {
    if (!page) {
      throw new Error('No active browser page. Call launch_browser first.');
    }
    
    logger.info(`Running ${steps.length} steps`);
    
    const results = [];
    const artifacts = {
      screenshots: [],
      videos: [],
      traces: []
    };
    
    for (const step of steps) {
      const startTime = Date.now();
      let stepResult = { name: Object.keys(step)[0], status: 'passed' };
      
      try {
        const [action, params] = Object.entries(step)[0];
        
        switch (action) {
          case 'goto':
            await page.goto(params, { waitUntil: 'networkidle' });
            break;
          case 'click':
            await page.click(params);
            break;
          case 'fill':
            await page.fill(params.selector, params.value);
            break;
          case 'assert':
            await page.waitForSelector(params.selector, { 
              state: params.state || 'visible',
              timeout: params.timeout || 5000
            });
            break;
          case 'screenshot':
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const screenshotPath = path.join(ARTIFACT_DIR, `step-${results.length + 1}-${timestamp}.png`);
            await page.screenshot({ path: screenshotPath, fullPage: true });
            artifacts.screenshots.push(screenshotPath);
            break;
          default:
            throw new Error(`Unknown action: ${action}`);
        }
      } catch (err) {
        stepResult.status = 'failed';
        stepResult.error = err.message;
        
        // Capture failure screenshot
        try {
          const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
          const screenshotPath = path.join(ARTIFACT_DIR, `failure-${results.length + 1}-${timestamp}.png`);
          await page.screenshot({ path: screenshotPath, fullPage: true });
          artifacts.screenshots.push(screenshotPath);
          stepResult.screenshot = screenshotPath;
        } catch (screenshotErr) {
          logger.error(`Failed to capture failure screenshot: ${screenshotErr.message}`);
        }
      }
      
      stepResult.durationMs = Date.now() - startTime;
      results.push(stepResult);
      
      // Stop execution if a step fails
      if (stepResult.status === 'failed') {
        break;
      }
    }
    
    const status = results.some(r => r.status === 'failed') ? 'failed' : 'passed';
    const report = {
      status,
      steps: results,
      artifacts
    };
    
    return report;
  } catch (err) {
    logger.error(`Failed to run steps: ${err.message}`);
    return { 
      status: 'error',
      error: err.message 
    };
  }
});

// Performance metrics
server.addTool('get_performance_metrics', 'Collect performance metrics from the page', async () => {
  try {
    if (!page) {
      throw new Error('No active browser page. Call launch_browser first.');
    }
    
    logger.info('Collecting performance metrics');
    
    // Get core web vitals and performance metrics
    const metrics = await page.evaluate(() => {
      // Basic performance metrics
      const perfEntries = performance.getEntriesByType('navigation');
      const navEntry = perfEntries.length ? perfEntries[0] : {};
      
      // Core Web Vitals may not be available in all contexts
      const coreWebVitals = {};
      if ('web-vitals' in window) {
        // This would require injecting the web-vitals library
        // In real implementation, we would inject this script first
      }
      
      return {
        timing: {
          navigationStart: navEntry.startTime || 0,
          loadEventEnd: navEntry.loadEventEnd || 0,
          domContentLoaded: navEntry.domContentLoadedEventEnd || 0,
          firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
          firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
        },
        memory: performance.memory ? {
          jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
          totalJSHeapSize: performance.memory.totalJSHeapSize,
          usedJSHeapSize: performance.memory.usedJSHeapSize
        } : {},
        coreWebVitals
      };
    });
    
    return { 
      success: true,
      metrics 
    };
  } catch (err) {
    logger.error(`Failed to get performance metrics: ${err.message}`);
    return { success: false, error: err.message };
  }
});

// --- Signal Handling for graceful shutdown ---
function handleSignal(signal) {
  logger.info(`Received ${signal} signal, shutting down gracefully...`);
  
  // Close any active browser sessions
  if (browserContext) {
    try {
      browserContext.close().catch(err => {
        logger.error(`Error closing browser context: ${err.message}`);
      });
    } catch (err) {
      logger.error(`Error in browser cleanup: ${err.message}`);
    }
  }
  
  // Allow some time for cleanup operations before exiting
  setTimeout(() => {
    logger.info('Cleanup complete, exiting now');
    process.exit(0);
  }, 1000);
}

// Register signal handlers
process.on('SIGINT', () => handleSignal('SIGINT'));
process.on('SIGTERM', () => handleSignal('SIGTERM'));

// Handle uncaught errors without crashing
process.on('uncaughtException', (err) => {
  logger.error(`Uncaught exception: ${err.message}\n${err.stack}`);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error(`Unhandled rejection at: ${promise}, reason: ${reason}`);
});

// --- Start the server ---
logger.info('Test Automation MCP Server started');

// Just keep the process running - our readline interface handles the messages
process.stdin.resume();