# 🚀 VIBETEST MANUAL INSTALLATION GUIDE

## Option 1: Command Prompt Installation (Recommended)

Open **Command Prompt** and run these commands one by one:

```cmd
pip install browser-use
pip install langchain-google-genai  
pip install playwright
pip install screeninfo
pip install fastmcp

python -m playwright install chromium

cd "C:\AI_Projects\Claude-MCP-tools\servers\vibetest-use"
pip install -e .
```

## Option 2: Windows Batch Script

Run this file as Administrator:
```
C:\AI_Projects\Claude-MCP-tools\servers\vibetest-use\install_windows.bat
```

## Option 3: PowerShell (Alternative)

```powershell
py -m pip install browser-use langchain-google-genai playwright screeninfo fastmcp
py -m playwright install chromium
cd "C:\AI_Projects\Claude-MCP-tools\servers\vibetest-use"
py -m pip install -e .
```

## Verification

After installation, verify with:
```cmd
python -c "import browser_use; print('✅ browser-use installed')"
python -c "import langchain_google_genai; print('✅ langchain-google-genai installed')" 
python -c "import playwright; print('✅ playwright installed')"
```

## Next Steps

1. ✅ **Dependencies installed** (above steps)
2. 🔑 **Get Google API Key**: https://aistudio.google.com/app/apikey
3. ⚙️ **Update Claude Config**: Replace `YOUR_GOOGLE_API_KEY_HERE` with real key
4. 🔄 **Restart Claude Desktop**
5. 🧪 **Start Testing**: "Test https://example.com for UI bugs using 3 agents"

## Troubleshooting

- **Permission errors**: Run Command Prompt as Administrator
- **pip not found**: Use `py -m pip` instead of `pip`
- **Long timeouts**: Install packages one by one
- **Import errors**: Restart Claude Desktop after installation

The vibetest server is ready to spawn browser agents and test websites! 🎯
