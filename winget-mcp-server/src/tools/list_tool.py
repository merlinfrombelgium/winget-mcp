#!/usr/bin/env python3
"""WinGet list tool implementation"""

import subprocess
import asyncio
import json
import re
from typing import List, Dict, Any

async def list_installed(count: int = 20) -> Dict[str, Any]:
    """
    List installed packages using WinGet
    
    Args:
        count: Maximum number of results to return
        
    Returns:
        Dictionary containing installed packages and metadata
    """
    try:
        # Build WinGet list command
        cmd = ['winget', 'list', '--accept-source-agreements']
        
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
                "error": f"WinGet list failed: {stderr}",
                "packages": []
            }
        
        # Parse the output
        packages = parse_list_output(stdout)
        
        return {
            "success": True,
            "count_requested": count,
            "count_returned": len(packages[:count]),
            "total_installed": len(packages),
            "packages": packages[:count]  # Return only requested count
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"List error: {str(e)}",
            "packages": []
        }

def parse_list_output(output: str) -> List[Dict[str, str]]:
    """
    Parse WinGet list output into structured data
    
    Args:
        output: Raw WinGet list output
        
    Returns:
        List of installed package dictionaries
    """
    packages = []
    lines = output.strip().split('\n')
    
    # Find the header line (contains "Name", "Id", "Version", etc.)
    header_line_idx = -1
    for i, line in enumerate(lines):
        if 'Name' in line and 'Id' in line and 'Version' in line:
            header_line_idx = i
            break
    
    if header_line_idx == -1:
        return packages
    
    # Find separator line (dashes)
    separator_idx = -1
    for i in range(header_line_idx + 1, len(lines)):
        if lines[i].strip().startswith('-'):
            separator_idx = i
            break
    
    if separator_idx == -1:
        return packages
    
    # Parse package lines
    for line in lines[separator_idx + 1:]:
        line = line.strip()
        if not line:
            continue
            
        # Split by multiple spaces to separate columns
        parts = re.split(r'\s{2,}', line)
        
        if len(parts) >= 2:
            package = {
                "name": parts[0].strip(),
                "id": parts[1].strip() if len(parts) > 1 else "Unknown",
                "version": parts[2].strip() if len(parts) > 2 else "Unknown",
                "available": parts[3].strip() if len(parts) > 3 else None,
                "source": parts[4].strip() if len(parts) > 4 else "Unknown"
            }
            packages.append(package)
    
    return packages
