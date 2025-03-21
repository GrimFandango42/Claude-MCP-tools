import streamlit as st
import requests
import json
import base64
import os
import time
from PIL import Image
import io

# Set page configuration
st.set_page_config(
    page_title="Claude Desktop Bridge",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define API URL and headers
API_URL = os.getenv("API_URL", "http://localhost:8000/api")
API_KEY = os.getenv("API_KEY", "")

headers = {}
if API_KEY:
    headers["X-API-Key"] = API_KEY

# Initialize session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "screenshot" not in st.session_state:
    st.session_state.screenshot = None

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = """
    You are Claude, an AI assistant with the ability to control the user's computer.
    You have access to the following tools:
    
    1. Computer control: Take screenshots, click, type, press keys, move the mouse, scroll, and drag.
    2. Browser automation: Navigate to URLs, click on elements, type text, extract content, search the web.
    3. System integration: Execute commands, launch applications, get system information.
    
    When the user asks you to perform an action on their computer, use the appropriate tool.
    Always be helpful, respectful, and mindful of the user's security and privacy.
    """

# Functions
def take_screenshot():
    """Take a screenshot using the bridge API"""
    try:
        response = requests.post(
            f"{API_URL}/computer/screenshot",
            json={"full_screen": True},
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        
        # Save screenshot to session state
        st.session_state.screenshot = result
        
        return result
    except Exception as e:
        st.error(f"Error taking screenshot: {str(e)}")
        return None

def analyze_screenshot(image_data):
    """Analyze a screenshot using Claude Vision"""
    try:
        response = requests.post(
            f"{API_URL}/computer/analyze",
            json={"image_data": image_data},
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        
        return result
    except Exception as e:
        st.error(f"Error analyzing screenshot: {str(e)}")
        return None

def send_message(message, system=None):
    """Send a message to Claude and handle any tool use"""
    # Add user message to conversation
    st.session_state.conversation.append({"role": "user", "content": message})
    
    # Prepare request payload
    payload = {
        "messages": st.session_state.conversation,
        "model": "claude-3-opus-20240229",
        "max_tokens": 4096
    }
    
    if system:
        payload["system"] = system
    
    # Send message to Claude via bridge
    try:
        with st.spinner("Claude is thinking..."):
            response = requests.post(
                f"{API_URL}/bridge/message",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            claude_response = response.json()
            
            # Process Claude's response
            return process_claude_response(claude_response)
    except Exception as e:
        st.error(f"Error sending message to Claude: {str(e)}")
        return f"Error: {str(e)}"

def process_claude_response(response):
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
    
    # Add assistant response to conversation
    st.session_state.conversation.append({
        "role": "assistant",
        "content": content
    })
    
    # Handle any tool uses
    tool_results = []
    for tool_use in tool_uses:
        tool_name = tool_use.get("name")
        tool_params = tool_use.get("input", {})
        tool_id = tool_use.get("id")
        
        st.info(f"Claude is using tool: {tool_name}\nParameters: {json.dumps(tool_params, indent=2)}")
        
        # Call the tool via bridge
        tool_result = call_tool(tool_name, tool_params, tool_id)
        tool_results.append(tool_result)
        
        # Add tool result to conversation
        st.session_state.conversation.append({
            "role": "tool",
            "tool_use_id": tool_id,
            "content": json.dumps(tool_result)
        })
    
    # If tools were used, send a follow-up message to Claude
    if tool_results:
        st.info("Tools were used. Getting Claude's final response...")
        return get_final_response()
    
    return response_text

def call_tool(tool_name, parameters, message_id):
    """Call a tool via the bridge API"""
    try:
        with st.spinner(f"Executing tool: {tool_name}..."):
            response = requests.post(
                f"{API_URL}/bridge/tool_use",
                json={
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "message_id": message_id
                },
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            st.success(f"Tool executed successfully: {tool_name}")
            return result.get("result", {})
    except Exception as e:
        error_msg = f"Error calling tool {tool_name}: {str(e)}"
        st.error(error_msg)
        return {"error": error_msg}

def get_final_response():
    """Get Claude's final response after tool use"""
    # Prepare request payload
    payload = {
        "messages": st.session_state.conversation,
        "model": "claude-3-opus-20240229",
        "max_tokens": 4096
    }
    
    # Send message to Claude via bridge
    try:
        with st.spinner("Claude is thinking..."):
            response = requests.post(
                f"{API_URL}/bridge/message",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            claude_response = response.json()
            
            # Extract text from response
            content = claude_response.get("content", [])
            response_text = ""
            
            for block in content:
                if block.get("type") == "text":
                    response_text += block.get("text", "")
            
            # Add assistant response to conversation
            st.session_state.conversation.append({
                "role": "assistant",
                "content": content
            })
            
            return response_text
    except Exception as e:
        st.error(f"Error getting final response from Claude: {str(e)}")
        return f"Error: {str(e)}"

def clear_conversation():
    """Clear the conversation history"""
    st.session_state.conversation = []
    st.success("Conversation history cleared.")

# Sidebar
st.sidebar.title("Claude Desktop Bridge")
st.sidebar.image("https://www.anthropic.com/images/icons/favicon.svg", width=100)

# System prompt editor
st.sidebar.subheader("System Prompt")
system_prompt = st.sidebar.text_area(
    "Edit the system prompt for Claude",
    value=st.session_state.system_prompt,
    height=200
)
st.session_state.system_prompt = system_prompt

# Tools section
st.sidebar.subheader("Tools")

# Screenshot tool
if st.sidebar.button("Take Screenshot"):
    screenshot = take_screenshot()
    if screenshot:
        st.sidebar.success("Screenshot taken successfully!")

# Analyze screenshot button
if st.session_state.screenshot and st.sidebar.button("Analyze Screenshot"):
    analysis = analyze_screenshot(st.session_state.screenshot["image_data"])
    if analysis:
        st.sidebar.success("Screenshot analyzed successfully!")
        st.sidebar.text_area("Analysis", value=analysis.get("description", ""), height=200)

# Clear conversation button
if st.sidebar.button("Clear Conversation"):
    clear_conversation()

# Check API connection
st.sidebar.subheader("API Status")
try:
    response = requests.get(f"{API_URL.split('/api')[0]}/health")
    if response.status_code == 200:
        st.sidebar.success("Connected to API")
    else:
        st.sidebar.error("API connection error")
except Exception:
    st.sidebar.error("Cannot connect to API")

# Main content
st.title("Claude Desktop Agent")

# Display screenshot if available
if st.session_state.screenshot:
    st.subheader("Latest Screenshot")
    image_data = st.session_state.screenshot["image_data"]
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))
    st.image(image, caption="Current Desktop Screenshot", use_column_width=True)

# Display conversation
st.subheader("Conversation")
for message in st.session_state.conversation:
    role = message.get("role")
    content = message.get("content")
    
    if role == "user":
        st.markdown(f"**You:** {content}")
    elif role == "assistant":
        if isinstance(content, list):
            # Process content blocks
            for block in content:
                if block.get("type") == "text":
                    st.markdown(f"**Claude:** {block.get('text', '')}")
                elif block.get("type") == "tool_use":
                    tool_name = block.get("name")
                    st.markdown(f"**Claude is using tool:** {tool_name}")
        else:
            st.markdown(f"**Claude:** {content}")
    elif role == "tool":
        st.markdown(f"**Tool Result:** {content}")

# User input
st.subheader("Send a message to Claude")
user_input = st.text_area("Your message", height=100)

if st.button("Send"):
    if user_input:
        # Display user message
        st.markdown(f"**You:** {user_input}")
        
        # Get Claude's response
        with st.spinner("Claude is thinking..."):
            response = send_message(user_input, st.session_state.system_prompt)
        
        # Display Claude's response
        st.markdown(f"**Claude:** {response}")
    else:
        st.warning("Please enter a message.")

# Footer
st.markdown("---")
st.markdown("Claude Desktop Bridge - Powered by Anthropic's Claude API")
