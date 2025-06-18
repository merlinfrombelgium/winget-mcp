#!/usr/bin/env python3
"""Generate Cursor MCP configuration for WinGet server"""

import json
import os
import sys
from pathlib import Path

def get_project_paths():
    """Get the correct paths for the current project"""
    # Get current directory (should be winget-mcp-server)
    current_dir = Path.cwd()
    
    # Get the project root (parent of winget-mcp-server)
    project_root = current_dir.parent
    
    # Paths for the configuration
    python_exe = current_dir / ".venv" / "Scripts" / "python.exe"
    main_py = current_dir / "main.py"
    src_dir = current_dir / "src"
    
    return {
        "project_root": str(project_root),
        "server_dir": str(current_dir),
        "python_exe": str(python_exe),
        "main_py": str(main_py),
        "src_dir": str(src_dir)
    }

def generate_config():
    """Generate the MCP configuration"""
    paths = get_project_paths()
    
    # Basic configuration
    config = {
        "mcpServers": {
            "winget": {
                "command": paths["python_exe"],
                "args": [paths["main_py"]],
                "env": {
                    "PYTHONPATH": paths["src_dir"]
                }
            }
        }
    }
    
    return config

def generate_alternative_configs():
    """Generate alternative configuration options"""
    paths = get_project_paths()
    
    configs = {}
    
    # Option 1: Full paths
    configs["full_paths"] = {
        "mcpServers": {
            "winget": {
                "command": paths["python_exe"],
                "args": [paths["main_py"]],
                "env": {
                    "PYTHONPATH": paths["src_dir"]
                }
            }
        }
    }
    
    # Option 2: Using working directory
    configs["with_cwd"] = {
        "mcpServers": {
            "winget": {
                "command": paths["python_exe"],
                "args": ["main.py"],
                "cwd": paths["server_dir"],
                "env": {
                    "PYTHONPATH": "src"
                }
            }
        }
    }
    
    # Option 3: System Python (if venv issues)
    configs["system_python"] = {
        "mcpServers": {
            "winget": {
                "command": "python",
                "args": [paths["main_py"]],
                "cwd": paths["server_dir"],
                "env": {
                    "PYTHONPATH": paths["src_dir"]
                }
            }
        }
    }
    
    return configs

def find_cursor_config_location():
    """Find the likely Cursor configuration location"""
    import os
    
    # Windows paths to check
    possible_paths = [
        os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage"),
        os.path.expanduser(r"~\AppData\Roaming\Cursor\User\globalStorage"),
        os.path.expanduser(r"~\.cursor\globalStorage"),
    ]
    
    existing_paths = []
    for path in possible_paths:
        if os.path.exists(path):
            existing_paths.append(path)
    
    return existing_paths

def main():
    """Main function"""
    print("🔧 Cursor MCP Configuration Generator")
    print("=" * 50)
    
    # Get paths
    paths = get_project_paths()
    
    print("\n📂 Detected Paths:")
    for key, value in paths.items():
        exists = "✅" if os.path.exists(value) else "❌"
        print(f"   {key}: {exists} {value}")
    
    # Check if virtual environment exists
    if not os.path.exists(paths["python_exe"]):
        print("\n⚠️  Warning: Virtual environment not found!")
        print("   Run: uv venv && uv pip install -e .")
        return
    
    # Generate configurations
    print("\n🎯 Generated Configurations:")
    print("-" * 30)
    
    config = generate_config()
    alternatives = generate_alternative_configs()
    
    # Save main configuration
    config_file = "cursor-mcp-config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Main configuration saved to: {config_file}")
    print("\n📋 Configuration content:")
    print(json.dumps(config, indent=2))
    
    # Save alternatives
    for name, alt_config in alternatives.items():
        alt_file = f"cursor-mcp-config-{name}.json"
        with open(alt_file, 'w') as f:
            json.dump(alt_config, f, indent=2)
        print(f"\n💡 Alternative '{name}' saved to: {alt_file}")
    
    # Find Cursor config location
    print("\n📍 Cursor Configuration Locations:")
    cursor_paths = find_cursor_config_location()
    
    if cursor_paths:
        for path in cursor_paths:
            mcp_file = os.path.join(path, "mcp.json")
            exists = "✅ EXISTS" if os.path.exists(mcp_file) else "📝 CREATE"
            print(f"   {exists}: {mcp_file}")
    else:
        print("   ❌ No Cursor directories found")
        print("   Create manually at: %APPDATA%\\Cursor\\User\\globalStorage\\mcp.json")
    
    # Instructions
    print("\n🚀 Next Steps:")
    print("1. Copy the configuration content above")
    print("2. Paste it into Cursor's mcp.json file")
    print("3. Update paths if needed for your system")
    print("4. Restart Cursor")
    print("5. Test the WinGet MCP server connection")
    
    print(f"\n📖 For detailed instructions, see: CURSOR_SETUP.md")

if __name__ == "__main__":
    main() 