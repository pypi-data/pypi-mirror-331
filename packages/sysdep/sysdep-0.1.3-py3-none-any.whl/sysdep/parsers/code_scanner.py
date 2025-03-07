# sysdep/parsers/code_scanner.py
# Standard library imports
import os
import re
from typing import List, Set, Optional

# Local imports
from ..checkers.base import Dependency
from ..checkers.executable import ExecutableDependency
from ..config import COMMON_DEPENDENCIES
from ..utils import with_progress, parallel_map

class DependencyScanner:
    """
    Scan Python code for annotations indicating system dependencies.
    
    Looks for special comments like:
    # sysdep: ffmpeg >= 4.2.0
    # requires-system: imagemagick
    """
    
    COMMENT_PATTERNS = [
        r'#\s*sysdep:\s*([\w\-\.]+)(?:\s*(>=|==|>)\s*([\d\.]+))?',
        r'#\s*requires-system:\s*([\w\-\.]+)(?:\s*(>=|==|>)\s*([\d\.]+))?',
    ]
    
    def __init__(self):
        self.found_dependencies = set()
        
    def scan_file(self, file_path: str) -> Set[Dependency]:
        """Scan a single Python file for dependency annotations."""
        if not os.path.exists(file_path) or not file_path.endswith('.py'):
            return set()
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        dependencies = set()
        
        # Look for comment annotations
        for pattern in self.COMMENT_PATTERNS:
            for match in re.finditer(pattern, content):
                name, operator, version = match.groups()
                
                # Check if we have a predefined common dependency
                if name.lower() in COMMON_DEPENDENCIES:
                    common_def = COMMON_DEPENDENCIES[name.lower()]
                    dep = ExecutableDependency(
                        name=common_def['name'],
                        version=version,
                        version_flag=common_def.get('version_flag', '--version'),
                        version_regex=common_def.get('version_regex'),
                        operator=operator
                    )
                else:
                    # Generic executable dependency
                    dep = ExecutableDependency(
                        name=name,
                        version=version,
                        operator=operator
                    )
                
                dependencies.add(dep)
                
        return dependencies
    
    def scan_directory(self, directory: str, recursive: bool = True, show_progress: bool = True, max_workers: Optional[int] = None) -> Set[Dependency]:
        """
        Scan a directory for Python files containing dependency annotations.
        
        Args:
            directory: Path to the directory to scan
            recursive: Whether to recursively scan subdirectories
            show_progress: Whether to show a progress bar during scanning
            max_workers: Maximum number of worker threads for parallel processing
            
        Returns:
            Set of found dependencies
        """
        if not os.path.isdir(directory):
            return set()
            
        all_files = []
        for root, dirs, files in os.walk(directory):
            if not recursive and root != directory:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    all_files.append(os.path.join(root, file))
        
        # Reset found dependencies
        self.found_dependencies = set()
        
        # Scan files in parallel
        results = parallel_map(
            self.scan_file,
            all_files,
            desc="Scanning files",
            show_progress=show_progress,
            max_workers=max_workers
        )
        
        # Combine all dependencies
        for deps in results:
            if deps:
                self.found_dependencies.update(deps)
            
        return self.found_dependencies