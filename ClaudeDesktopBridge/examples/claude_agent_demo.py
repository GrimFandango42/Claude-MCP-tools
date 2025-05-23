import os
import sys
import requests
import json
import base64
import time
from PIL import Image
import io

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ClaudeDesktopAgent:
    def __init__(self, api_url, anthropic_api_key=None, bridge_api_key=None):
        self.api_url = api_url
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.bridge_api_key = bridge_api_key or os.getenv("API_KEY")
        self.headers = {}
        if self.bridge_api_key:
            self.headers["X-API-Key"] = self.bridge_api_key
        
        self.conversation_history = []
        self.tools_enabled = True
    
    def send_message(self, message, system=None):
        """Send a message to Claude and handle any tool use"""
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Prepare request payload
        payload = {
            "messages": self.conversation_history,
            "model": "claude-3-opus-20240229",
            "max_tokens": 4096
        }
        
        if system:
            payload["system"] = system
        
        # Send message to Claude via bridge
        try:
            response = requests.post(
                f"{self.api_url}/bridge/message",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            claude_response = response.json()
            
            # Process Claude's response
            return self._process_claude_response(claude_response)
            
        except Exception as e:
            print(f"Error sending message to Claude: {str(e)}")
            return f"Error: {str(e)}"
    
    def _process_claude_response(self, response):
        """Process Claude's response, handling any tool use"""
        # Extract response content
        content = response.get("content", [])
        response_text = ""
        tool_uses = []
        
        # Process each content block
        for block in content:
            if block.get("type") == "text":
                response_text += block.get("text", "")
            elif block.get("type") == "tool_use":
                tool_uses.append(block)
        
        # Add assistant response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": content
        })
        
        # Handle any tool uses
        tool_results = []
        for tool_use in tool_uses:
            tool_name = tool_use.get("name")
            tool_params = tool_use.get("input", {})
            tool_id = tool_use.get("id")
            
            print(f"\nClaude is using tool: {tool_name}")
            print(f"Parameters: {json.dumps(tool_params, indent=2)}")
            
            # Call the tool via bridge
            tool_result = self._call_tool(tool_name, tool_params, tool_id)
            tool_results.append(tool_result)
            
            # Add tool result to conversation history
            self.conversation_history.append({
                "role": "tool",
                "tool_use_id": tool_id,
                "content": json.dumps(tool_result)
            })
        
        # If tools were used, send a follow-up message to Claude
        if tool_results:
            print("\nTools were used. Getting Claude's final response...")
            return self._get_final_response()
        
        return response_text
    
    def _call_tool(self, tool_name, parameters, message_id):
        """Call a tool via the bridge API"""
        try:
            response = requests.post(
                f"{self.api_url}/bridge/tool_use",
                json={
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "message_id": message_id
                },
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"Tool result: {json.dumps(result.get('result', {}), indent=2)}")
            return result.get("result", {})
            
        except Exception as e:
            error_msg = f"Error calling tool {tool_name}: {str(e)}"
            print(error_msg)
            return {"error": error_msg}
    
    def _get_final_response(self):
        """Get Claude's final response after tool use"""
        # Prepare request payload
        payload = {
            "messages": self.conversation_history,
            "model": "claude-3-opus-20240229",
            "max_tokens": 4096
        }
        
        # Send message to Claude via bridge
        try:
            response = requests.post(
                f"{self.api_url}/bridge/message",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            claude_response = response.json()
            
            # Extract text from response
            content = claude_response.get("content", [])
            response_text = ""
            
            for block in content:
                if block.get("type") == "text":
                    response_text += block.get("text", "")
            
            # Add assistant response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": content
            })
            
            return response_text
            
        except Exception as e:
            print(f"Error getting final response from Claude: {str(e)}")
            return f"Error: {str(e)}"
    
    def take_screenshot(self):
        """Take a screenshot using the bridge API"""
        try:
            response = requests.post(
                f"{self.api_url}/computer/screenshot",
                json={"full_screen": True},
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            # Save screenshot to file
            image_data = result.get("image_data")
            if image_data:
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                image.save(filename)
                print(f"Screenshot saved to {filename}")
            
            return result
            
        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")
            return None
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
        print("Conversation history cleared.")

def main():
    # Configuration
    api_url = "http://localhost:8000/api"
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    bridge_api_key = os.getenv("API_KEY")
    
    if not anthropic_api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        return
    
    # Create Claude Desktop Agent
    agent = ClaudeDesktopAgent(api_url, anthropic_api_key, bridge_api_key)
    
    # System prompt for Claude
    system_prompt = """
    You are Claude, an AI assistant with the ability to control the user's computer.
    You have access to the following tools:
    
    1. Computer control: Take screenshots, click, type, press keys, move the mouse, scroll, and drag.
    2. Browser automation: Navigate to URLs, click on elements, type text, extract content, search the web.
    3. System integration: Execute commands, launch applications, get system information.
    
    When the user asks you to perform an action on their computer, use the appropriate tool.
    Always be helpful, respectful, and mindful of the user's security and privacy.
    """
    
    print("Claude Desktop Agent Demo")
    print("=" * 50)
    print("Type 'exit' to quit, 'clear' to clear conversation history, or 'screenshot' to take a screenshot.")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "clear":
            agent.clear_conversation()
            continue
        elif user_input.lower() == "screenshot":
            agent.take_screenshot()
            continue
        
        print("\nClaude: ", end="")
        response = agent.send_message(user_input, system_prompt)
        print(response)

if __name__ == "__main__":
    main()
