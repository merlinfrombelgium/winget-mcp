# WinGet MCP Server

A Model Context Protocol (MCP) server that provides WinGet package management capabilities for Windows.

## Overview

This MCP server allows AI assistants to interact with Windows Package Manager (WinGet) to search, install, and manage software packages on Windows systems.

## Prerequisites

- **Windows 10/11** with WinGet installed
- **Python 3.13+**
- **UV package manager** (recommended) or pip
- **Administrator privileges** (for some WinGet operations)

## Quick Start

### 1. Installation

Navigate to the server directory and set up the environment:

```bash
cd winget-mcp-server
uv venv
uv pip install -e .
```

Or with pip:
```bash
cd winget-mcp-server
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### 2. Running the Server

#### Method 1: Using main.py (Recommended)
```bash
uv run python main.py
```

#### Method 2: Direct server execution
```bash
uv run python src/server.py
```

#### Method 3: As a module
```bash
uv run python -m src.server
```

### 3. Verify Installation

Test that WinGet is accessible:
```bash
winget --version
```

## Usage with MCP Clients

This server implements the MCP protocol and can be used with any MCP-compatible client (Claude Desktop, etc.).

### Example Client Configuration

Add to your MCP client configuration file:

```json
{
  "mcpServers": {
    "winget-mcp-server": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "C:/path/to/winget-mcp-server"
    }
  }
}
```

## Available Tools

Once fully implemented, this server will provide:

- **winget_search**: Search for packages in WinGet repositories
- **winget_install**: Install packages using WinGet  
- **winget_list**: List installed packages
- **winget_info**: Get detailed package information
- **winget_upgrade**: Upgrade installed packages
- **winget_uninstall**: Remove installed packages

## Development

### Project Structure
```
winget-mcp-server/
├── src/
│   ├── server.py          # Main server implementation
│   ├── tools/             # MCP tool implementations
│   │   ├── search_tool.py
│   │   ├── install_tool.py
│   │   ├── list_tool.py
│   │   └── info_tool.py
│   ├── utils/             # Utility modules
│   ├── security/          # Security validation
│   └── winget_manager.py  # WinGet command interface
├── tests/                 # Test files
├── main.py               # Entry point
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

### Running Tests
```bash
uv run python -m pytest tests/ -v
```

### Development Setup
```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run linting
uv run ruff check src/

# Run type checking
uv run mypy src/
```

## Security Considerations

- This server can execute system commands through WinGet
- Ensure proper validation of package names and sources
- Consider running with appropriate user permissions
- Review security policies in `src/security/`

## Troubleshooting

### Server Won't Start
1. Verify WinGet is installed: `winget --version`
2. Check Python version: `python --version` (should be 3.13+)
3. Ensure dependencies are installed: `uv pip install -e .`
4. Check for error messages in terminal output

### Permission Issues
- Run terminal as Administrator for system-wide package operations
- Check Windows execution policies: `Get-ExecutionPolicy`
- Verify WinGet permissions and user account settings

### Package Installation Fails
- Ensure package names are correct (use `winget search` first)
- Check internet connectivity
- Verify package source availability
- Review WinGet logs for detailed error information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run the test suite
5. Submit a pull request

## License

[Specify your license here]

## Support

For issues and questions:
- Check the troubleshooting section above
- Review WinGet documentation
- File issues in the project repository
