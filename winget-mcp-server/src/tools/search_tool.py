#!/usr/bin/env python3
"""WinGet search tool implementation"""

import subprocess
import asyncio
import json
import re
from typing import List, Dict, Any

async def search_packages(query: str, count: int = 10) -> Dict[str, Any]:
    """
    Search for packages using WinGet
    
    Args:
        query: Search term or package name
        count: Maximum number of results to return
        
    Returns:
        Dictionary containing search results and metadata
    """
    try:
        # Build WinGet search command
        cmd = ['winget', 'search', query, '--count', str(count), '--accept-source-agreements']
        
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
                "error": f"WinGet search failed: {stderr}",
                "packages": []
            }
        
        # Parse the output
        packages = parse_search_output(stdout)
        
        return {
            "success": True,
            "query": query,
            "count_requested": count,
            "count_returned": len(packages),
            "packages": packages[:count]  # Ensure we don't exceed requested count
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Search error: {str(e)}",
            "packages": []
        }

def parse_search_output(output: str) -> List[Dict[str, str]]:
    """
    Parse WinGet search output into structured data
    
    Args:
        output: Raw WinGet search output
        
    Returns:
        List of package dictionaries
    """
    packages = []
    
    # Clean up the output - remove carriage returns and extra whitespace/control chars
    cleaned_output = output.replace('\r', '').strip()
    
    # Split into lines and clean them up
    lines = []
    for line in cleaned_output.split('\n'):
        line = line.strip()
        if line:  # Only keep non-empty lines
            lines.append(line)
    
    # Find the header line (contains "Name", "Id", "Version", "Source")
    header_line_idx = -1
    for i, line in enumerate(lines):
        if 'Name' in line and 'Id' in line and 'Version' in line:
            header_line_idx = i
            break
    
    if header_line_idx == -1:
        return packages
    
    # Find separator line (dashes) - it's usually the next line after header
    separator_idx = -1
    for i in range(header_line_idx + 1, len(lines)):
        if lines[i].startswith('-'):
            separator_idx = i
            break
    
    if separator_idx == -1:
        # If no separator found, assume data starts right after header
        separator_idx = header_line_idx
    
    # Get column positions from the header line
    header_line = lines[header_line_idx]
    name_start = header_line.find('Name')
    id_start = header_line.find('Id')
    version_start = header_line.find('Version')
    source_start = header_line.find('Source')
    
    # Parse package lines using fixed positions
    for line in lines[separator_idx + 1:]:
        line = line.strip()
        
        # Skip empty lines, separator lines, or lines with special content
        if not line or line.startswith('-') or line.startswith('<') or 'truncated' in line.lower():
            continue
        
        # Extract columns based on positions
        try:
            name = line[name_start:id_start].strip() if id_start > name_start else line[:id_start].strip()
            id_val = line[id_start:version_start].strip() if version_start > id_start else line[id_start:source_start].strip()
            version = line[version_start:source_start].strip() if source_start > version_start else "Unknown"
            source = line[source_start:].strip() if source_start < len(line) else "winget"
            
            if name and id_val and len(name) > 0 and len(id_val) > 0:
                package = {
                    "name": name,
                    "id": id_val,
                    "version": version if version else "Unknown",
                    "source": source if source else "winget"
                }
                packages.append(package)
        except Exception as e:
            # Skip lines that can't be parsed properly
            continue
    
    return packages
