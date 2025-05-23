import sys
import os
import base64
import json
import unittest
from fastapi.testclient import TestClient
from PIL import Image
import io

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.modules.computer import ComputerModule

# Create test client
client = TestClient(app)

class TestComputerModule(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.computer_module = ComputerModule()
        self.screenshots_dir = self.computer_module.screenshots_dir
        
        # Ensure screenshots directory exists
        os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def test_capture_screenshot(self):
        """Test screenshot capture functionality"""
        # Capture screenshot
        result = self.computer_module.capture_screenshot()
        
        # Check if result contains expected keys
        self.assertIn('image_data', result)
        self.assertIn('width', result)
        self.assertIn('height', result)
        self.assertIn('timestamp', result)
        
        # Check if width and height are positive integers
        self.assertGreater(result['width'], 0)
        self.assertGreater(result['height'], 0)
        
        # Check if image_data is a valid base64 string
        try:
            image_bytes = base64.b64decode(result['image_data'])
            image = Image.open(io.BytesIO(image_bytes))
            self.assertIsInstance(image, Image.Image)
        except Exception as e:
            self.fail(f"Failed to decode image data: {str(e)}")
    
    def test_api_screenshot_endpoint(self):
        """Test screenshot API endpoint"""
        # Send request to API
        response = client.post(
            "/api/computer/screenshot",
            json={"full_screen": True}
        )
        
        # Check if response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check if response contains expected keys
        data = response.json()
        self.assertIn('image_data', data)
        self.assertIn('width', data)
        self.assertIn('height', data)
        
        # Check if width and height are positive integers
        self.assertGreater(data['width'], 0)
        self.assertGreater(data['height'], 0)

class TestMouseControl(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.computer_module = ComputerModule()
    
    def test_mouse_move(self):
        """Test mouse movement functionality"""
        try:
            # Move mouse to center of screen
            screen_width, screen_height = self.computer_module.capture_screenshot()['width'], self.computer_module.capture_screenshot()['height']
            center_x, center_y = screen_width // 2, screen_height // 2
            
            # Move mouse to center
            self.computer_module.mouse_move(center_x, center_y)
            
            # Test passed if no exception was raised
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Mouse move failed: {str(e)}")
    
    def test_api_mouse_move_endpoint(self):
        """Test mouse move API endpoint"""
        # Get screen dimensions
        screenshot_response = client.post(
            "/api/computer/screenshot",
            json={"full_screen": True}
        )
        screenshot_data = screenshot_response.json()
        center_x, center_y = screenshot_data['width'] // 2, screenshot_data['height'] // 2
        
        # Send request to API
        response = client.post(
            "/api/computer/mouse_move",
            json={"x": center_x, "y": center_y}
        )
        
        # Check if response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check if response indicates success
        data = response.json()
        self.assertTrue(data['success'])

if __name__ == "__main__":
    unittest.main()
