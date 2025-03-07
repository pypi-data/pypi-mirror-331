# sysdep/checkers/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any

class Dependency(ABC):
    """Base class for system dependencies."""
    
    def __init__(self, name: str, version: Optional[str] = None, aliases: Optional[List[str]] = None):
        self.name = name
        self.version = version
        self.aliases = aliases or []
        
    @abstractmethod
    def is_installed(self) -> bool:
        """Check if the dependency is installed."""
        pass
    
    @abstractmethod
    def get_installation_info(self) -> Dict[str, Any]:
        """Get installation information for this dependency."""
        pass
    
    def to_manifest_line(self) -> str:
        """Convert the dependency to a manifest file line format."""
        # Get the type from the class name (e.g., ExecutableDependency -> executable)
        dep_type = self.__class__.__name__.lower().replace('dependency', '')
        
        if self.version:
            return f"{dep_type}: {self.name} >= {self.version}"
        return f"{dep_type}: {self.name}"
    
    def __str__(self) -> str:
        if self.version:
            return f"{self.name} (>= {self.version})"
        return self.name