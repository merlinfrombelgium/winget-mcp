# Adding WinGet MCP Server to Cursor

This guide shows you how to add your WinGet MCP server to Cursor's MCP configuration.

## 🔧 Setup Steps

### 1. Locate Cursor's MCP Configuration File

The MCP configuration file location depends on your operating system:

**Windows:**
```
%APPDATA%\Cursor\User\globalStorage\mcp.json
```

**Alternative Windows locations:**
```
C:\Users\[USERNAME]\AppData\Roaming\Cursor\User\globalStorage\mcp.json
```

### 2. Create or Edit mcp.json

If the file doesn't exist, create it. If it exists, add the winget server to the existing configuration.

**Complete Configuration:**
```json
{
  "mcpServers": {
    "winget": {
      "command": "X:\\projects\\winget-mcp\\winget-mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["X:\\projects\\winget-mcp\\winget-mcp-server\\main.py"],
      "env": {
        "PYTHONPATH": "X:\\projects\\winget-mcp\\winget-mcp-server\\src"
      }
    }
  }
}
```

**If you already have other MCP servers:**
```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "winget": {
      "command": "X:\\projects\\winget-mcp\\winget-mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["X:\\projects\\winget-mcp\\winget-mcp-server\\main.py"],
      "env": {
        "PYTHONPATH": "X:\\projects\\winget-mcp\\winget-mcp-server\\src"
      }
    }
  }
}
```

### 3. Update Paths for Your System

**Important:** Update the paths in the configuration to match your actual system:

1. Replace `X:\\projects\\winget-mcp` with your actual project path
2. Ensure the Python executable path is correct
3. Verify the main.py path is accurate

**To find your exact paths:**
```bash
# In your project directory
cd winget-mcp-server
pwd  # Shows current directory
.venv\Scripts\python.exe --version  # Verifies Python path
```

### 4. Restart Cursor

After saving the mcp.json file:
1. Close Cursor completely
2. Restart Cursor
3. Your WinGet MCP server should now be available

## 🧪 Testing in Cursor

### 1. Verify Server Connection

In Cursor, you should be able to:
- See the WinGet server in MCP server list
- Connect to the server without errors
- Access WinGet functionality through MCP tools

### 2. Test Commands

Once connected, you can test with commands like:
- Search for packages
- List installed software
- Get package information
- Install packages (with proper permissions)

## 🔍 Troubleshooting

### Common Issues:

**1. Server Not Found:**
- Check that all paths in mcp.json are correct
- Ensure the virtual environment exists
- Verify Python executable is accessible

**2. Permission Errors:**
- Run Cursor as administrator for package installations
- Check Windows execution policy for PowerShell

**3. Server Fails to Start:**
- Test the server manually first: `python main.py`
- Check dependencies are installed: `pip list | findstr mcp`
- Verify WinGet is available: `winget --version`

### Debug Steps:

1. **Test server manually:**
   ```bash
   cd winget-mcp-server
   .venv\Scripts\activate
   python main.py
   ```

2. **Check Cursor logs:**
   - Look for MCP-related errors in Cursor's developer console
   - Check if the server process starts correctly

3. **Verify configuration:**
   ```bash
   # Test the exact command Cursor will use
   "X:\projects\winget-mcp\winget-mcp-server\.venv\Scripts\python.exe" "X:\projects\winget-mcp\winget-mcp-server\main.py"
   ```

## 📝 Configuration Templates

### Minimal Configuration:
```json
{
  "mcpServers": {
    "winget": {
      "command": "python",
      "args": ["X:\\projects\\winget-mcp\\winget-mcp-server\\main.py"],
      "cwd": "X:\\projects\\winget-mcp\\winget-mcp-server"
    }
  }
}
```

### Full Configuration with Environment:
```json
{
  "mcpServers": {
    "winget": {
      "command": "X:\\projects\\winget-mcp\\winget-mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["main.py"],
      "cwd": "X:\\projects\\winget-mcp\\winget-mcp-server",
      "env": {
        "PYTHONPATH": "src",
        "PATH": "X:\\projects\\winget-mcp\\winget-mcp-server\\.venv\\Scripts;${PATH}"
      }
    }
  }
}
```

## ✅ Success Indicators

When properly configured, you should see:
- ✅ WinGet server appears in Cursor's MCP server list
- ✅ Server status shows as "Connected" or "Running"
- ✅ No error messages in Cursor's console
- ✅ MCP tools are available for use

## 🚀 Next Steps

After successful setup:
1. Test basic WinGet operations through Cursor
2. Implement additional WinGet tools as needed
3. Configure tool permissions and security settings
4. Share the configuration with your team 