import os
import sys
import requests
import base64
import json
from PIL import Image
import io
import time

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def take_and_analyze_screenshot(api_url, api_key=None):
    """Take a screenshot and analyze it using Claude Vision"""
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    # Take screenshot
    print("Taking screenshot...")
    screenshot_response = requests.post(
        f"{api_url}/computer/screenshot",
        json={"full_screen": True},
        headers=headers
    )
    
    if screenshot_response.status_code != 200:
        print(f"Error taking screenshot: {screenshot_response.text}")
        return None
    
    screenshot_data = screenshot_response.json()
    image_data = screenshot_data["image_data"]
    
    # Display screenshot dimensions
    print(f"Screenshot dimensions: {screenshot_data['width']}x{screenshot_data['height']}")
    
    # Save screenshot to file
    try:
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        image.save(filename)
        print(f"Screenshot saved to {filename}")
    except Exception as e:
        print(f"Error saving screenshot: {str(e)}")
    
    # Analyze screenshot with Claude
    print("\nAnalyzing screenshot with Claude...")
    analyze_response = requests.post(
        f"{api_url}/computer/analyze",
        json={"image_data": image_data},
        headers=headers
    )
    
    if analyze_response.status_code != 200:
        print(f"Error analyzing screenshot: {analyze_response.text}")
        return None
    
    analysis_data = analyze_response.json()
    description = analysis_data.get("description", "No description available")
    
    print("\nClaude's analysis:")
    print("-" * 50)
    print(description)
    print("-" * 50)
    
    return {
        "screenshot": screenshot_data,
        "analysis": analysis_data
    }

def perform_mouse_click(api_url, x, y, api_key=None):
    """Perform a mouse click at the specified coordinates"""
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    print(f"Clicking at coordinates ({x}, {y})...")
    click_response = requests.post(
        f"{api_url}/computer/click",
        json={"x": x, "y": y, "button": "left", "clicks": 1},
        headers=headers
    )
    
    if click_response.status_code != 200:
        print(f"Error performing click: {click_response.text}")
        return False
    
    click_data = click_response.json()
    print(f"Click result: {click_data['message']}")
    return True

def type_text(api_url, text, api_key=None):
    """Type text at the current cursor position"""
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    print(f"Typing text: {text}")
    type_response = requests.post(
        f"{api_url}/computer/type",
        json={"text": text},
        headers=headers
    )
    
    if type_response.status_code != 200:
        print(f"Error typing text: {type_response.text}")
        return False
    
    type_data = type_response.json()
    print(f"Type result: {type_data['message']}")
    return True

def main():
    # Configuration
    api_url = "http://localhost:8000/api"
    api_key = os.getenv("API_KEY", "")
    
    print("Claude Desktop Bridge - Screenshot Demo")
    print("=" * 50)
    
    # Take and analyze screenshot
    result = take_and_analyze_screenshot(api_url, api_key)
    
    if result:
        # Ask user if they want to perform a mouse click
        click_choice = input("\nWould you like to perform a mouse click? (y/n): ")
        if click_choice.lower() == "y":
            try:
                x = int(input("Enter X coordinate: "))
                y = int(input("Enter Y coordinate: "))
                perform_mouse_click(api_url, x, y, api_key)
            except ValueError:
                print("Invalid coordinates. Must be integers.")
        
        # Ask user if they want to type text
        type_choice = input("\nWould you like to type some text? (y/n): ")
        if type_choice.lower() == "y":
            text = input("Enter text to type: ")
            type_text(api_url, text, api_key)
    
    print("\nDemo completed.")

if __name__ == "__main__":
    main()
