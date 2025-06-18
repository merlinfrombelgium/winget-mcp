#!/usr/bin/env python3
"""WinGet MCP Server - Main server implementation using FastMCP"""

import asyncio
import json
import sys
import os
from typing import Annotated, Optional
from pydantic import Field
from mcp.server.fastmcp import FastMCP

# Add src directory to Python path to ensure tools can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create the FastMCP server instance
mcp = FastMCP("winget-mcp-server")

@mcp.tool()
async def winget_search(
    query: Annotated[str, Field(description="Search term or package name to find in WinGet repositories")], 
    count: Annotated[int, Field(description="Maximum number of search results to return", ge=1, le=50)] = 10
) -> str:
    """Search for packages in WinGet repositories"""
    try:
        from tools.search_tool import search_packages
        result = await search_packages(query, count)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"}, indent=2)

@mcp.tool()
async def winget_list(
    count: Annotated[int, Field(description="Maximum number of installed packages to return", ge=1, le=100)] = 20
) -> str:
    """List installed packages"""
    try:
        from tools.list_tool import list_installed
        result = await list_installed(count)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"List failed: {str(e)}"}, indent=2)

@mcp.tool()
async def winget_info(
    package_id: Annotated[str, Field(description="Package identifier (ID) to get detailed information about")]
) -> str:
    """Get detailed information about a package"""
    try:
        from tools.info_tool import get_package_info
        result = await get_package_info(package_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Info failed: {str(e)}"}, indent=2)

@mcp.tool()
async def winget_install(
    package_id: Annotated[str, Field(description="Package identifier (ID) to install")],
    version: Annotated[Optional[str], Field(description="Specific version to install (optional, uses latest if not specified)")] = None,
    silent: Annotated[bool, Field(description="Install silently without user interaction")] = True
) -> str:
    """Install a package using WinGet"""
    try:
        from tools.install_tool import install_package
        result = await install_package(package_id, version, silent)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Install failed: {str(e)}"}, indent=2)

if __name__ == "__main__":
    mcp.run()
