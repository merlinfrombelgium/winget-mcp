#!/usr/bin/env python3
"""WinGet info tool implementation"""

import subprocess
import asyncio
import json
import re
from typing import Dict, Any

async def get_package_info(package_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a package using WinGet
    
    Args:
        package_id: Package ID to get information for
        
    Returns:
        Dictionary containing package information
    """
    try:
        # Build WinGet show command
        cmd = ['winget', 'show', package_id, '--accept-source-agreements']
        
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
        
        if process.returncode != 0:
            return {
                "success": False,
                "error": f"WinGet show failed: {stderr}",
                "package_id": package_id,
                "info": {}
            }
        
        # Parse the output
        info = parse_info_output(stdout)
        
        return {
            "success": True,
            "package_id": package_id,
            "info": info
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Info error: {str(e)}",
            "package_id": package_id,
            "info": {}
        }

def parse_info_output(output: str) -> Dict[str, str]:
    """
    Parse WinGet show output into structured data
    
    Args:
        output: Raw WinGet show output
        
    Returns:
        Dictionary of package information
    """
    info = {}
    lines = output.strip().split('\n')
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a section header (no colon, usually title case)
        if ':' not in line and line.replace(' ', '').isalnum():
            current_section = line
            continue
        
        # Parse key-value pairs
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                
                # Add section prefix if we're in a section
                if current_section and current_section.lower() not in key.lower():
                    full_key = f"{current_section}_{key}".replace(' ', '_').lower()
                else:
                    full_key = key.replace(' ', '_').lower()
                
                info[full_key] = value
    
    # Clean up and standardize some common fields
    standardized_info = {}
    
    # Map common fields to standard names
    field_mapping = {
        'found': 'name',
        'version': 'version',
        'publisher': 'publisher',
        'description': 'description',
        'homepage': 'homepage',
        'license': 'license',
        'download_url': 'download_url',
        'installer_type': 'installer_type',
        'installer_url': 'installer_url'
    }
    
    for key, value in info.items():
        # Try to map to standard field names
        mapped_key = None
        for pattern, standard_name in field_mapping.items():
            if pattern in key.lower():
                mapped_key = standard_name
                break
        
        if mapped_key:
            standardized_info[mapped_key] = value
        else:
            standardized_info[key] = value
    
    return standardized_info
