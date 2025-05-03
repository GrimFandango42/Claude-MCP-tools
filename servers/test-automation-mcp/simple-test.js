/**
 * Simple Test for Test Automation MCP Server
 * 
 * This script tests basic functionality without complex interactions.
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('Starting simple test for Test Automation MCP Server');

// Create artifact directory if it doesn't exist
const fs = require('fs');
const artifactDir = path.join(__dirname, 'artifacts');
if (!fs.existsSync(artifactDir)) {
  fs.mkdirSync(artifactDir, { recursive: true });
  console.log(`Created artifact directory: ${artifactDir}`);
}

// Load the Playwright library directly to ensure it works
try {
  const playwright = require('@playwright/test');
  console.log('Successfully loaded Playwright library');
  
  // Try to launch a browser to verify Playwright works
  async function testPlaywright() {
    try {
      console.log('Attempting to launch browser with Playwright...');
      const browser = await playwright.chromium.launch({ headless: true });
      console.log('Browser launched successfully');
      
      const context = await browser.newContext();
      const page = await context.newPage();
      
      console.log('Navigating to example.com...');
      await page.goto('https://example.com');
      console.log('Navigation successful');
      
      // Take a screenshot
      const screenshotPath = path.join(artifactDir, 'example-test.png');
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.log(`Screenshot saved to: ${screenshotPath}`);
      
      // Check for an element
      const heading = await page.$('h1');
      if (heading) {
        console.log('Found h1 element on page');
      } else {
        console.log('Could not find h1 element');
      }
      
      // Close browser
      await browser.close();
      console.log('Browser closed successfully');
      
      return true;
    } catch (err) {
      console.error(`Playwright test failed: ${err.message}`);
      console.error(err.stack);
      return false;
    }
  }
  
  // Run the test
  testPlaywright().then(success => {
    if (success) {
      console.log('\n✅ Playwright functionality test PASSED');
    } else {
      console.log('\n❌ Playwright functionality test FAILED');
    }
    
    console.log('\nTesting server.js manually would require handling the JSON-RPC protocol.');
    console.log('For manual testing, run:');
    console.log('  node test-server.js');
    console.log('And follow the interactive prompts to test specific features.');
    
    process.exit(success ? 0 : 1);
  });
} catch (err) {
  console.error(`Failed to load Playwright: ${err.message}`);
  console.error('Please install Playwright with: npm install @playwright/test');
  process.exit(1);
}