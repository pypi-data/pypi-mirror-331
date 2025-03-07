# sysdep/platforms/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class PlatformManager(ABC):
    """Base class for platform-specific operations."""
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Get the platform ID."""
        pass
        
    @abstractmethod
    def is_current_platform(self) -> bool:
        """Check if this is the current platform."""
        pass
        
    @abstractmethod
    def get_installation_commands(self, package_name: str) -> List[str]:
        """Get commands to install a package on this platform."""
        pass
        
    @abstractmethod
    def install_package(self, package_name: str) -> bool:
        """Install a package on this platform."""
        pass