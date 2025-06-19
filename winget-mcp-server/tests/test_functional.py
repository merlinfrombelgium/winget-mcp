#!/usr/bin/env python3
"""Functional tests for WinGet MCP Server"""

import asyncio
import json
import sys
import os
import unittest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server import mcp

class TestWinGetMCPFunctional(unittest.TestCase):
    """Functional tests for WinGet MCP Server tools"""
    
    async def async_test_search_tool(self):
        """Test winget_search tool functionality"""
        # Test with a common package
        search_args = {"query": "python", "count": 3}
        result = await mcp.call_tool("winget_search", search_args)
        
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        
        # Parse response
        response_text = result[0].text
        response_data = json.loads(response_text)
        
        # Validate response structure
        self.assertIn('success', response_data)
        self.assertIn('query', response_data)
        self.assertIn('count_requested', response_data)
        self.assertIn('count_returned', response_data)
        self.assertIn('packages', response_data)
        
        # Validate query matches
        self.assertEqual(response_data['query'], 'python')
        self.assertEqual(response_data['count_requested'], 3)
        
        # Validate packages structure
        if response_data['success'] and response_data['count_returned'] > 0:
            packages = response_data['packages']
            self.assertIsInstance(packages, list)
            
            # Check first package structure
            if packages:
                pkg = packages[0]
                self.assertIn('name', pkg)
                self.assertIn('id', pkg)
                self.assertIn('version', pkg)
                self.assertIn('source', pkg)
        
        return response_data
    
    def test_search_tool(self):
        """Test search tool (sync wrapper)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.async_test_search_tool())
            self.assertIsNotNone(result)
        finally:
            loop.close()
    
    async def async_test_list_tool(self):
        """Test winget_list tool functionality"""
        list_args = {"count": 5}
        result = await mcp.call_tool("winget_list", list_args)
        
        self.assertIsNotNone(result)
        response_text = result[0].text
        response_data = json.loads(response_text)
        
        # Should have basic structure even if no packages installed
        self.assertIn('success', response_data)
        self.assertIn('packages', response_data)
        
        return response_data
    
    def test_list_tool(self):
        """Test list tool (sync wrapper)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.async_test_list_tool())
            self.assertIsNotNone(result)
        finally:
            loop.close()
    
    async def async_test_info_tool(self):
        """Test winget_info tool functionality"""
        # Test with a known package ID (Microsoft.PowerShell is commonly available)
        info_args = {"package_id": "Microsoft.PowerShell"}
        result = await mcp.call_tool("winget_info", info_args)
        
        self.assertIsNotNone(result)
        response_text = result[0].text
        response_data = json.loads(response_text)
        
        # Should have basic structure
        self.assertIn('success', response_data)
        
        return response_data
    
    def test_info_tool(self):
        """Test info tool (sync wrapper)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.async_test_info_tool())
            self.assertIsNotNone(result)
        finally:
            loop.close()
    
    async def async_test_install_tool_dry_run(self):
        """Test winget_install tool functionality (dry run)"""
        # Test with a package but don't actually install
        # This tests the tool structure without making system changes
        install_args = {"package_id": "NonExistentPackage.Test", "silent": True}
        result = await mcp.call_tool("winget_install", install_args)
        
        self.assertIsNotNone(result)
        response_text = result[0].text
        response_data = json.loads(response_text)
        
        # Should have basic structure (will likely fail but structure should be there)
        self.assertIn('success', response_data)
        
        return response_data
    
    def test_install_tool_dry_run(self):
        """Test install tool dry run (sync wrapper)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.async_test_install_tool_dry_run())
            self.assertIsNotNone(result)
        finally:
            loop.close()
    
    async def async_test_all_tools_registration(self):
        """Test that all tools are properly registered and accessible"""
        tools = await mcp.list_tools()
        
        # Test each tool can be called
        results = {}
        
        # Test search
        search_result = await mcp.call_tool("winget_search", {"query": "test", "count": 1})
        results['search'] = json.loads(search_result[0].text)
        
        # Test list  
        list_result = await mcp.call_tool("winget_list", {"count": 1})
        results['list'] = json.loads(list_result[0].text)
        
        # Test info
        info_result = await mcp.call_tool("winget_info", {"package_id": "test"})
        results['info'] = json.loads(info_result[0].text)
        
        # Test install (dry run)
        install_result = await mcp.call_tool("winget_install", {"package_id": "test", "silent": True})
        results['install'] = json.loads(install_result[0].text)
        
        # All should have responded (even if with errors)
        for tool_name, result in results.items():
            self.assertIn('success', result, f"Tool {tool_name} missing success field")
        
        return results
    
    def test_all_tools_registration(self):
        """Test all tools registration and basic execution (sync wrapper)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(self.async_test_all_tools_registration())
            self.assertEqual(len(results), 4, "Should have results from all 4 tools")
        finally:
            loop.close()

class TestMCPProtocolCompliance(unittest.TestCase):
    """Test MCP protocol compliance"""
    
    def test_server_name(self):
        """Test server has correct name"""
        self.assertEqual(mcp.name, "winget-mcp-server")
    
    async def async_test_tools_schema(self):
        """Test that tools have proper MCP schema"""
        tools = await mcp.list_tools()
        
        for tool in tools:
            # Each tool should have required fields
            self.assertTrue(hasattr(tool, 'name'))
            self.assertTrue(hasattr(tool, 'description'))
            self.assertTrue(hasattr(tool, 'inputSchema'))
            
            # Name should be string
            self.assertIsInstance(tool.name, str)
            self.assertTrue(len(tool.name) > 0)
            
            # Description should be string
            self.assertIsInstance(tool.description, str)
            self.assertTrue(len(tool.description) > 0)
            
            # Input schema should be dict-like
            self.assertIsNotNone(tool.inputSchema)
        
        return True
    
    def test_tools_schema(self):
        """Test tools schema (sync wrapper)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.async_test_tools_schema())
            self.assertTrue(result)
        finally:
            loop.close()

if __name__ == '__main__':
    # Run with high verbosity to see detailed test results
    unittest.main(verbosity=2)
