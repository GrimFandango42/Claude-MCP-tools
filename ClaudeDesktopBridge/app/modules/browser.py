import os
import base64
import io
from PIL import Image
from typing import Dict, Any, List, Optional, Tuple, Literal
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from app.utils.logger import setup_logger
from app.utils.config import settings

# Setup logger
logger = setup_logger(__name__)

class BrowserModule:
    def __init__(self):
        self.driver = None
        self.screenshots_dir = settings.SCREENSHOTS_DIR
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
            logger.info(f"Created screenshots directory at {self.screenshots_dir}")
    
    async def _ensure_driver(self):
        """Ensure that the browser driver is initialized"""
        if self.driver is None:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Initialize Chrome driver
            logger.info("Initializing Chrome driver")
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            logger.info("Chrome driver initialized")
    
    async def navigate(self, url: str, wait_until: Literal["load", "domcontentloaded", "networkidle"] = "networkidle", 
                    timeout: int = 30000) -> Dict[str, Any]:
        """Navigate to a URL"""
        try:
            # Ensure driver is initialized
            await self._ensure_driver()
            
            # Navigate to URL
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load based on wait_until parameter
            if wait_until == "load":
                # Wait for document.readyState to be 'complete'
                WebDriverWait(self.driver, timeout / 1000).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            elif wait_until == "domcontentloaded":
                # Wait for document.readyState to be at least 'interactive'
                WebDriverWait(self.driver, timeout / 1000).until(
                    lambda d: d.execute_script("return document.readyState") in ["interactive", "complete"]
                )
            elif wait_until == "networkidle":
                # Wait for document.readyState to be 'complete' and then a bit more for network to be idle
                WebDriverWait(self.driver, timeout / 1000).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                # Additional wait to allow for any AJAX requests to complete
                await asyncio.sleep(1)
            
            # Get page title
            title = self.driver.title
            
            return {"url": url, "title": title}
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}", exc_info=True)
            raise
    
    async def click(self, selector: str, timeout: int = 5000, button: Literal["left", "right", "middle"] = "left") -> None:
        """Click on an element"""
        try:
            # Ensure driver is initialized
            await self._ensure_driver()
            
            # Wait for element to be clickable
            logger.info(f"Waiting for element to be clickable: {selector}")
            element = WebDriverWait(self.driver, timeout / 1000).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            # Click element
            if button == "left":
                element.click()
            else:
                # For right or middle click, use JavaScript or ActionChains
                if button == "right":
                    self.driver.execute_script(
                        "arguments[0].dispatchEvent(new MouseEvent('contextmenu', {bubbles: true}));", 
                        element
                    )
                elif button == "middle":
                    # Middle click isn't directly supported in Selenium, so we use JavaScript
                    self.driver.execute_script(
                        "arguments[0].dispatchEvent(new MouseEvent('auxclick', {bubbles: true, button: 1}));", 
                        element
                    )
            
            logger.info(f"Clicked on element: {selector}")
        except TimeoutException:
            logger.error(f"Timeout waiting for element to be clickable: {selector}")
            raise
        except Exception as e:
            logger.error(f"Error clicking on element {selector}: {str(e)}", exc_info=True)
            raise
    
    async def type(self, selector: str, text: str, delay: int = 50) -> None:
        """Type text into an element"""
        try:
            # Ensure driver is initialized
            await self._ensure_driver()
            
            # Wait for element to be present
            logger.info(f"Waiting for element to be present: {selector}")
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            # Clear existing text
            element.clear()
            
            # Type text with delay
            for char in text:
                element.send_keys(char)
                if delay > 0:
                    await asyncio.sleep(delay / 1000)  # Convert milliseconds to seconds
            
            logger.info(f"Typed text into element: {selector}")
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {selector}")
            raise
        except Exception as e:
            logger.error(f"Error typing into element {selector}: {str(e)}", exc_info=True)
            raise
    
    async def extract(self, selector: Optional[str] = None, xpath: Optional[str] = None, 
                    attribute: Optional[str] = None, include_html: bool = False) -> Dict[str, Any]:
        """Extract content from the page"""
        try:
            # Ensure driver is initialized
            await self._ensure_driver()
            
            elements = []
            
            # Find elements by selector or xpath
            if selector:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            elif xpath:
                elements = self.driver.find_elements(By.XPATH, xpath)
            else:
                # If no selector or xpath provided, get the entire page body
                elements = [self.driver.find_element(By.TAG_NAME, "body")]
            
            # Extract text and optionally HTML and attributes
            text_list = []
            html_list = []
            attributes_list = []
            
            for element in elements:
                # Extract text
                text_list.append(element.text)
                
                # Extract HTML if requested
                if include_html:
                    html_list.append(element.get_attribute("outerHTML"))
                
                # Extract specific attribute if requested
                if attribute:
                    attr_value = element.get_attribute(attribute)
                    attributes_list.append({attribute: attr_value})
            
            result = {"text": text_list}
            
            if include_html:
                result["html"] = html_list
            
            if attribute:
                result["attributes"] = attributes_list
            
            return result
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}", exc_info=True)
            raise
    
    async def search(self, query: str, engine: Literal["google", "bing", "duckduckgo"] = "google") -> List[Dict[str, str]]:
        """Perform a web search"""
        try:
            # Ensure driver is initialized
            await self._ensure_driver()
            
            # Determine search URL based on engine
            if engine == "google":
                search_url = f"https://www.google.com/search?q={query}"
            elif engine == "bing":
                search_url = f"https://www.bing.com/search?q={query}"
            elif engine == "duckduckgo":
                search_url = f"https://duckduckgo.com/?q={query}"
            
            # Navigate to search URL
            await self.navigate(search_url)
            
            # Extract search results based on engine
            results = []
            
            if engine == "google":
                # Wait for search results to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
                )
                
                # Extract search results
                search_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
                
                for element in search_elements[:10]:  # Limit to first 10 results
                    try:
                        title_element = element.find_element(By.CSS_SELECTOR, "h3")
                        link_element = element.find_element(By.CSS_SELECTOR, "a")
                        snippet_element = element.find_element(By.CSS_SELECTOR, "div.VwiC3b")
                        
                        title = title_element.text
                        link = link_element.get_attribute("href")
                        snippet = snippet_element.text
                        
                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet
                        })
                    except NoSuchElementException:
                        # Skip results that don't match the expected format
                        continue
            
            elif engine == "bing":
                # Wait for search results to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li.b_algo"))
                )
                
                # Extract search results
                search_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
                
                for element in search_elements[:10]:  # Limit to first 10 results
                    try:
                        title_element = element.find_element(By.CSS_SELECTOR, "h2 a")
                        snippet_element = element.find_element(By.CSS_SELECTOR, "p")
                        
                        title = title_element.text
                        link = title_element.get_attribute("href")
                        snippet = snippet_element.text
                        
                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet
                        })
                    except NoSuchElementException:
                        # Skip results that don't match the expected format
                        continue
            
            elif engine == "duckduckgo":
                # Wait for search results to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
                )
                
                # Extract search results
                search_elements = self.driver.find_elements(By.CSS_SELECTOR, "article")
                
                for element in search_elements[:10]:  # Limit to first 10 results
                    try:
                        title_element = element.find_element(By.CSS_SELECTOR, "h2")
                        link_element = element.find_element(By.CSS_SELECTOR, "a.result__a")
                        snippet_element = element.find_element(By.CSS_SELECTOR, "div.result__snippet")
                        
                        title = title_element.text
                        link = link_element.get_attribute("href")
                        snippet = snippet_element.text
                        
                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet
                        })
                    except NoSuchElementException:
                        # Skip results that don't match the expected format
                        continue
            
            return results
        except Exception as e:
            logger.error(f"Error performing search for '{query}': {str(e)}", exc_info=True)
            raise
    
    async def screenshot(self, selector: Optional[str] = None, full_page: bool = False) -> Dict[str, Any]:
        """Take a screenshot of the page or an element"""
        try:
            # Ensure driver is initialized
            await self._ensure_driver()
            
            # Take screenshot
            if selector:
                # Find element
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                # Take screenshot of element
                screenshot = element.screenshot_as_png
                
                # Get element dimensions
                width = element.size["width"]
                height = element.size["height"]
            else:
                if full_page:
                    # Get page dimensions
                    width = self.driver.execute_script("return document.body.scrollWidth")
                    height = self.driver.execute_script("return document.body.scrollHeight")
                    
                    # Set window size to page dimensions
                    self.driver.set_window_size(width, height)
                
                # Take screenshot of entire page
                screenshot = self.driver.get_screenshot_as_png()
                
                # Get viewport dimensions
                width = self.driver.execute_script("return window.innerWidth")
                height = self.driver.execute_script("return window.innerHeight")
            
            # Convert to base64
            img_str = base64.b64encode(screenshot).decode()
            
            # Save screenshot to file
            timestamp = datetime.now().isoformat().replace(':', '-')
            filename = f"browser_screenshot_{timestamp}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(screenshot)
            
            logger.info(f"Saved browser screenshot to {filepath}")
            
            return {
                "image_data": img_str,
                "width": width,
                "height": height
            }
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}", exc_info=True)
            raise
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Browser closed")
