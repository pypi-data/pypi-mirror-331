"""
Core functionality for opening Windsurf instances.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def validate_paths(paths: List[str]) -> List[str]:
    """
    Validate that all provided paths exist.
    
    Args:
        paths: List of path strings to validate
        
    Returns:
        List of valid, absolute paths
    """
    valid_paths = []
    
    for path_str in paths:
        path = Path(path_str).expanduser().resolve()
        
        if not path.exists():
            print(f"Warning: Path does not exist: {path}", file=sys.stderr)
            continue
            
        valid_paths.append(str(path))
    
    return valid_paths


def open_windsurf(
    path: str, 
    wait: bool = False,
    user_data_dir: Optional[str] = None,
    profile: Optional[str] = None,
    new_window: bool = False
) -> subprocess.Popen:
    """
    Open a Windsurf instance for the specified path.
    
    Args:
        path: Path to open
        wait: Whether to wait for Windsurf to close
        user_data_dir: Custom user data directory
        profile: Profile to use
        new_window: Force opening in a new window
        
    Returns:
        Subprocess handle
    """
    cmd = ["windsurf"]
    
    if wait:
        cmd.append("--wait")
    
    if user_data_dir:
        cmd.extend(["--user-data-dir", user_data_dir])
    
    if profile:
        cmd.extend(["--profile", profile])
    
    if new_window:
        cmd.append("--new-window")
    
    cmd.append(path)
    
    print(f"Opening Windsurf for: {path}")
    return subprocess.Popen(cmd)
