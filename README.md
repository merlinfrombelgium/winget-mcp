# WinGet MCP Server

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org) [![FastMCP](https://img.shields.io/badge/FastMCP-1.9.4-green.svg)](https://github.com/jlowin/fastmcp) [![Tests](https://img.shields.io/badge/Tests-13%2F13%20Passing-brightgreen.svg)](#testing)

A production-ready Model Context Protocol (MCP) server that provides AI assistants with secure, controlled access to Windows Package Manager (WinGet) functionality.

## 🚀 Quick Start

```bash
cd winget-mcp-server
uv venv
uv pip install -e .
uv run python main.py
```

## 📋 Project Overview

This repository contains a complete MCP server implementation for WinGet package management, featuring:

- **🔧 4 Production Tools**: search, list, info, install
- **✅ 13/13 Tests Passing**: Comprehensive test coverage
- **🛡️ Security Model**: Input validation and safe command execution
- **�� Complete Documentation**: Memory Bank system with full project history
- **🌐 Multi-Platform Ready**: Python implementation with platform detection

## 🏗️ Repository Structure

### **Current Implementation (Python FastMCP)**
- **Location**: `winget-mcp-server/`
- **Status**: ✅ **Production Ready**
- **Framework**: Python FastMCP
- **Tests**: 13/13 passing

### **Future Implementation (C# .NET)**
- **Branch**: `dotnet-development`
- **Status**: 🚧 **Planned**
- **Framework**: C# with official MCP SDK
- **Advantage**: Native WinGet .NET API integration
