# sysdep/checkers/executable.py
import os
import shutil
import subprocess
from typing import Dict, List, Optional, Any
import re

from .base import Dependency
from ..platforms import get_platform_manager

class ExecutableDependency(Dependency):
    """Represents an executable command-line dependency."""
    
    def __init__(
        self, 
        name: str, 
        version: Optional[str] = None,
        version_flag: str = "--version",
        version_regex: str = r"(\d+\.\d+\.\d+)",
        aliases: Optional[List[str]] = None,
        package_names: Optional[Dict[str, str]] = None
    ):
        super().__init__(name, version, aliases)
        self.version_flag = version_flag
        self.version_regex = version_regex
        # Map platform IDs to package names (e.g., {'apt': 'imagemagick', 'brew': 'imagemagick'})
        self.package_names = package_names or {}
        
    def is_installed(self) -> bool:
        """Check if the executable is in PATH."""
        # Try the primary name
        if shutil.which(self.name):
            return True
        
        # Try aliases
        for alias in self.aliases:
            if shutil.which(alias):
                return True
                
        return False
        
    def get_installed_version(self) -> Optional[str]:
        """Get the installed version of the executable."""
        executable = self._get_executable_path()
        if not executable:
            return None
            
        try:
            result = subprocess.run(
                [executable, self.version_flag], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.returncode != 0:
                return None
                
            match = re.search(self.version_regex, result.stdout)
            if match:
                return match.group(1)
        except Exception:
            pass
            
        return None
        
    def _get_executable_path(self) -> Optional[str]:
        """Get the path to the executable, trying all aliases."""
        path = shutil.which(self.name)
        if path:
            return path
            
        for alias in self.aliases:
            path = shutil.which(alias)
            if path:
                return path
                
        return None
        
    def get_installation_info(self) -> Dict[str, Any]:
        """Get installation information for this executable."""
        platform = get_platform_manager()
        package_name = self.package_names.get(platform.id, self.name)
        
        return {
            "name": self.name,
            "type": "executable",
            "installed": self.is_installed(),
            "installed_version": self.get_installed_version(),
            "required_version": self.version,
            "package_name": package_name,
            "installation_commands": platform.get_installation_commands(package_name)
        }