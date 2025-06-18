#!/usr/bin/env python3
"""Entry point for WinGet MCP Server"""

if __name__ == "__main__":
    from src.server import mcp
    mcp.run()
