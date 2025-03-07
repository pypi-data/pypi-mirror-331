# sysdep/platforms/macos.py
import os
import subprocess
from typing import Dict, List, Optional

from .base import PlatformManager

class MacOSPlatformManager(PlatformManager):
    """Platform manager for macOS systems."""
    
    @property
    def id(self) -> str:
        return "brew"
        
    def is_current_platform(self) -> bool:
        import platform
        return platform.system().lower() == "darwin"
        
    def get_installation_commands(self, package_name: str) -> List[str]:
        return [
            f"brew update",
            f"brew install {package_name}"
        ]
        
    def install_package(self, package_name: str) -> bool:
        """Install a package using Homebrew."""
        try:
            # Check if Homebrew is installed
            if not self._check_brew_installed():
                return False
                
            # Update Homebrew
            subprocess.run(
                ["brew", "update"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Install the package
            subprocess.run(
                ["brew", "install", package_name],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return True
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return False
            
    def _check_brew_installed(self) -> bool:
        """Check if Homebrew is installed."""
        try:
            subprocess.run(
                ["brew", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False