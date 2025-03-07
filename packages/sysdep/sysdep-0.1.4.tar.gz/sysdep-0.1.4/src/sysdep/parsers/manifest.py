# sysdep/parsers/manifest.py
# Standard library imports
import os
import re
from typing import Dict, List, Optional, Any

# Local imports
from ..checkers.base import Dependency
from ..checkers.executable import ExecutableDependency
from ..checkers.library import LibraryDependency
from ..config import COMMON_DEPENDENCIES

def parse_manifest_file(file_path: str) -> List[Dependency]:
    """
    Parse a system requirements manifest file.
    
    The manifest file format is expected to be:
    # Comments start with hash
    executable: ffmpeg >= 4.2.0
    executable: imagemagick
    library: libssl >= 1.1.0
    
    Returns:
        List of Dependency objects
    """
    if not os.path.exists(file_path):
        return []
        
    dependencies = []
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            # Parse the line
            try:
                dep = _parse_manifest_line(line)
                if dep:
                    dependencies.append(dep)
            except ValueError as e:
                print(f"Warning: Error parsing line {line_num} in {file_path}: {e}")
                
    return dependencies

def _parse_manifest_line(line: str) -> Optional[Dependency]:
    """Parse a single line from the manifest file."""
    # Expected format: dependency_type: name [>= | == | > | =] version
    match = re.match(r'(\w+):\s*([\w\-\.]+)(?:\s*(>=|==|>|=)\s*([\d\.]+))?', line)
    
    if not match:
        raise ValueError(f"Invalid format: {line}")
        
    dep_type, name, operator, version = match.groups()
    
    # Normalize the operator if present
    if operator == '=':
        operator = '=='
    
    # Create the appropriate dependency object based on type
    if dep_type.lower() == 'executable':
        # Check if we have a predefined common dependency
        if name.lower() in COMMON_DEPENDENCIES:
            common_def = COMMON_DEPENDENCIES[name.lower()]
            dep = ExecutableDependency(
                name=common_def['name'],
                version=version,
                version_flag=common_def.get('version_flag', '--version'),
                version_regex=common_def.get('version_regex', r'(\d+\.\d+\.\d+)'),
                aliases=common_def.get('aliases', []),
                package_names=common_def.get('package_names', {})
            )
        else:
            # Create a generic executable dependency
            dep = ExecutableDependency(name=name, version=version)
        return dep
    elif dep_type.lower() == 'library':
        # Create a library dependency
        from ..checkers.library import LibraryDependency
        
        # Check if we have a predefined common dependency
        if name.lower() in COMMON_DEPENDENCIES and COMMON_DEPENDENCIES[name.lower()].get('type') == 'library':
            common_def = COMMON_DEPENDENCIES[name.lower()]
            dep = LibraryDependency(
                name=common_def['name'],
                version=version,
                pkg_config_name=common_def.get('pkg_config_name'),
                soname=common_def.get('soname'),
                aliases=common_def.get('aliases', []),
                package_names=common_def.get('package_names', {})
            )
        else:
            # Create a generic library dependency
            dep = LibraryDependency(name=name, version=version)
        return dep
    else:
        raise ValueError(f"Unknown dependency type: {dep_type}")