import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.modules.bridge import BridgeModule

# Create test client
client = TestClient(app)

class TestBridgeModule(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.bridge_module = BridgeModule()
    
    @patch('app.modules.bridge.requests.post')
    def test_send_message(self, mock_post):
        """Test sending a message to Claude API"""
        # Mock response from Claude API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "msg_123456789",
            "content": [{"type": "text", "text": "Hello, I'm Claude!"}],
            "model": "claude-3-opus-20240229",
            "role": "assistant",
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 10, "output_tokens": 20}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test sending a message
        messages = [{"role": "user", "content": "Hello, Claude!"}]
        result = self.bridge_module.send_message(messages, "claude-3-opus-20240229", 1024)
        
        # Check if result contains expected keys
        self.assertIn('id', result)
        self.assertIn('content', result)
        self.assertIn('model', result)
        self.assertIn('role', result)
        
        # Check if content is as expected
        self.assertEqual(result['content'][0]['text'], "Hello, I'm Claude!")
    
    @patch('app.modules.computer.ComputerModule.capture_screenshot')
    def test_handle_computer_tool(self, mock_capture_screenshot):
        """Test handling a computer tool request"""
        # Mock screenshot result
        mock_capture_screenshot.return_value = {
            "image_data": "base64_encoded_image_data",
            "width": 1920,
            "height": 1080,
            "timestamp": "2023-01-01T00:00:00"
        }
        
        # Test handling a screenshot request
        parameters = {"action": "screenshot", "full_screen": True}
        result = self.bridge_module._handle_computer_tool(parameters)
        
        # Check if result contains expected keys
        self.assertIn('image_data', result)
        self.assertIn('width', result)
        self.assertIn('height', result)
        
        # Check if width and height are as expected
        self.assertEqual(result['width'], 1920)
        self.assertEqual(result['height'], 1080)

class TestBridgeAPI(unittest.TestCase):
    @patch('app.modules.bridge.BridgeModule.handle_tool_use')
    def test_tool_use_endpoint(self, mock_handle_tool_use):
        """Test tool use API endpoint"""
        # Mock handle_tool_use result
        mock_handle_tool_use.return_value = {"success": True, "message": "Tool used successfully"}
        
        # Send request to API
        response = client.post(
            "/api/bridge/tool_use",
            json={
                "tool_name": "computer",
                "parameters": {"action": "screenshot", "full_screen": True},
                "message_id": "msg_123456789"
            },
            headers={"X-API-Key": os.getenv("API_KEY", "")}
        )
        
        # Check response status code
        # Note: If API_KEY is not set in environment, this will fail with 401
        if os.getenv("API_KEY", ""):
            self.assertEqual(response.status_code, 200)
            
            # Check if response contains expected keys
            data = response.json()
            self.assertIn('success', data)
            self.assertIn('message_id', data)
            self.assertIn('tool_name', data)
            self.assertIn('result', data)
            
            # Check if success is True
            self.assertTrue(data['success'])
        else:
            # Skip test if API_KEY is not set
            print("Skipping test_tool_use_endpoint: API_KEY not set")

if __name__ == "__main__":
    unittest.main()
