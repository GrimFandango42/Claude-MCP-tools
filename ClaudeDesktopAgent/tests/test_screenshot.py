import sys
import os
import unittest
import base64
from io import BytesIO
from PIL import Image

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.screenshot import ScreenshotModule

class TestScreenshotModule(unittest.TestCase):
    def setUp(self):
        self.screenshot_module = ScreenshotModule()
    
    def test_capture_screenshot(self):
        # Capture a screenshot
        result = self.screenshot_module.capture_screenshot()
        
        # Check that the result has the expected keys
        self.assertIn('image_data', result)
        self.assertIn('width', result)
        self.assertIn('height', result)
        self.assertIn('timestamp', result)
        
        # Check that width and height are positive integers
        self.assertGreater(result['width'], 0)
        self.assertGreater(result['height'], 0)
        
        # Check that image_data is a valid base64 string
        try:
            # Try to decode the base64 string
            image_bytes = base64.b64decode(result['image_data'])
            # Try to open it as an image
            image = Image.open(BytesIO(image_bytes))
            # Check that it's a valid image
            self.assertIsNotNone(image)
        except Exception as e:
            self.fail(f"Failed to decode image data: {str(e)}")

if __name__ == '__main__':
    unittest.main()
