#!/usr/bin/env python3
"""Test the FastMCP server functionality"""

import unittest
import sys
import os
import asyncio
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server import mcp

class TestFastMCPServer(unittest.TestCase):
    """Test the FastMCP server implementation"""
    
    def test_server_creation(self):
        """Test that FastMCP server instance exists"""
        self.assertIsNotNone(mcp)
        self.assertEqual(mcp.name, 'winget-mcp-server')
    
    def test_server_has_tool_methods(self):
        """Test that server has required MCP methods"""
        self.assertTrue(hasattr(mcp, 'list_tools'))
        self.assertTrue(hasattr(mcp, 'call_tool'))
        self.assertTrue(hasattr(mcp, 'run'))
    
    async def async_test_tools_registration(self):
        """Test that all 4 WinGet tools are registered"""
        tools = await mcp.list_tools()
        
        # Should have exactly 4 tools
        self.assertEqual(len(tools), 4)
        
        # Check tool names
        tool_names = [tool.name for tool in tools]
        expected_tools = ['winget_search', 'winget_list', 'winget_info', 'winget_install']
        
        for expected_tool in expected_tools:
            self.assertIn(expected_tool, tool_names, f"Tool {expected_tool} not found")
        
        # Check tool descriptions exist
        for tool in tools:
            self.assertIsNotNone(tool.description)
            self.assertTrue(len(tool.description) > 0)
            
        return tools
    
    def test_tools_registration(self):
        """Test tools registration (sync wrapper)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            tools = loop.run_until_complete(self.async_test_tools_registration())
            self.assertIsNotNone(tools)
        finally:
            loop.close()
    
    async def async_test_tool_execution(self):
        """Test that tools can be executed"""
        # Test winget_search tool
        search_args = {"query": "python", "count": 2}
        result = await mcp.call_tool("winget_search", search_args)
        
        # Should return TextContent
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, '__iter__'))  # Should be list-like
        
        if result:
            content = result[0]
            self.assertTrue(hasattr(content, 'text'))
            
            # Parse JSON response
            response_data = json.loads(content.text)
            self.assertIn('success', response_data)
            self.assertIn('query', response_data)
            self.assertEqual(response_data['query'], 'python')
        
        return True
    
    def test_tool_execution(self):
        """Test tool execution (sync wrapper)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.async_test_tool_execution())
            self.assertTrue(result)
        finally:
            loop.close()

class TestWinGetAvailability(unittest.TestCase):
    """Test WinGet availability and functionality"""
    
    def test_winget_available(self):
        """Test that WinGet is available on the system"""
        import subprocess
        try:
            result = subprocess.run(['winget', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, "WinGet should be available")
            self.assertIn('v', result.stdout.lower(), "WinGet version should contain 'v'")
        except FileNotFoundError:
            self.fail("WinGet not found - please install Windows Package Manager")
        except subprocess.TimeoutExpired:
            self.fail("WinGet command timed out")
    
    def test_winget_search_command(self):
        """Test that WinGet search command works"""
        import subprocess
        try:
            result = subprocess.run(['winget', 'search', 'python', '--count', '1'], 
                                  capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, "WinGet search should work")
            self.assertIn('Name', result.stdout, "WinGet output should contain header")
        except subprocess.TimeoutExpired:
            self.fail("WinGet search command timed out")

if __name__ == '__main__':
    # Run tests with more verbose output
    unittest.main(verbosity=2)
