import asyncio
import base64
import os
import sys
from datetime import datetime
from PIL import Image
import io

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the screenshot tool
from app.mcp.tools import ScreenshotTool

async def test_screenshot():
    print("Testing screenshot tool...")
    
    # Initialize the screenshot tool
    screenshot_tool = ScreenshotTool()
    
    # Take a full-screen screenshot
    print("Taking a full-screen screenshot...")
    result = await screenshot_tool.execute(full_screen=True)
    
    # Print the result metadata
    print(f"Screenshot taken at: {result['timestamp']}")
    print(f"Image dimensions: {result['width']}x{result['height']}")
    print(f"Saved to: {result['file_path']}")
    
    # Decode and display the image (optional)
    try:
        # Decode base64 image
        image_data = base64.b64decode(result['image_data'])
        image = Image.open(io.BytesIO(image_data))
        
        # Save a copy with a timestamp for verification
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Use absolute path for test output
        test_output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots", f"test_output_{timestamp}.png")
        image.save(test_output_path)
        print(f"Test image saved to: {test_output_path}")
        
        # On Windows, you can open the image with the default viewer
        print("Opening the image...")
        os.startfile(test_output_path)
    except Exception as e:
        print(f"Error displaying image: {e}")
    
    print("Screenshot test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_screenshot())
