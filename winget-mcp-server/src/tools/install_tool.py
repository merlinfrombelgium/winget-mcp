#!/usr/bin/env python3
"""WinGet install tool implementation"""

import subprocess
import asyncio
import json
from typing import Dict, Any, Optional

async def install_package(package_id: str, version: Optional[str] = None, silent: bool = True) -> Dict[str, Any]:
    """
    Install a package using WinGet
    
    Args:
        package_id: Package ID to install
        version: Specific version to install (optional)
        silent: Install silently without user interaction
        
    Returns:
        Dictionary containing installation result
    """
    try:
        # Build WinGet install command
        cmd = ['winget', 'install', package_id, '--accept-source-agreements', '--accept-package-agreements']
        
        if version:
            cmd.extend(['--version', version])
            
        if silent:
            cmd.append('--silent')
        
        # Execute the command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout_bytes, stderr_bytes = await process.communicate()
        
        # Decode bytes to string
        stdout = stdout_bytes.decode('utf-8', errors='ignore')
        stderr = stderr_bytes.decode('utf-8', errors='ignore')
        
        # Check result
        success = process.returncode == 0
        
        result = {
            "success": success,
            "package_id": package_id,
            "version": version,
            "silent": silent,
            "return_code": process.returncode,
            "stdout": stdout.strip(),
            "stderr": stderr.strip() if stderr else None
        }
        
        if success:
            result["message"] = f"Successfully installed {package_id}"
            if version:
                result["message"] += f" version {version}"
        else:
            result["error"] = f"Installation failed: {stderr or 'Unknown error'}"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Install error: {str(e)}",
            "package_id": package_id,
            "version": version,
            "silent": silent
        }

async def uninstall_package(package_id: str, silent: bool = True) -> Dict[str, Any]:
    """
    Uninstall a package using WinGet
    
    Args:
        package_id: Package ID to uninstall
        silent: Uninstall silently without user interaction
        
    Returns:
        Dictionary containing uninstallation result
    """
    try:
        # Build WinGet uninstall command
        cmd = ['winget', 'uninstall', package_id, '--accept-source-agreements']
        
        if silent:
            cmd.append('--silent')
        
        # Execute the command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout_bytes, stderr_bytes = await process.communicate()
        
        # Decode bytes to string
        stdout = stdout_bytes.decode('utf-8', errors='ignore')
        stderr = stderr_bytes.decode('utf-8', errors='ignore')
        
        # Check result
        success = process.returncode == 0
        
        result = {
            "success": success,
            "package_id": package_id,
            "silent": silent,
            "return_code": process.returncode,
            "stdout": stdout.strip(),
            "stderr": stderr.strip() if stderr else None
        }
        
        if success:
            result["message"] = f"Successfully uninstalled {package_id}"
        else:
            result["error"] = f"Uninstallation failed: {stderr or 'Unknown error'}"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Uninstall error: {str(e)}",
            "package_id": package_id,
            "silent": silent
        }
