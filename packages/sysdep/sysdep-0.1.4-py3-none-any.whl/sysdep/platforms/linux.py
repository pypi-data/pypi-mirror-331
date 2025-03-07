# sysdep/platforms/linux.py
import os
import subprocess
from typing import Dict, List, Optional

from .base import PlatformManager

class LinuxPlatformManager(PlatformManager):
    """Platform manager for Linux systems."""
    
    @property
    def id(self) -> str:
        return "apt"  # Default to apt, could be expanded to detect other package managers
        
    def is_current_platform(self) -> bool:
        import platform
        return platform.system().lower() == "linux"
        
    def get_installation_commands(self, package_name: str) -> List[str]:
        return [
            f"sudo apt-get update",
            f"sudo apt-get install -y {package_name}"
        ]
        
    def install_package(self, package_name: str) -> bool:
        """Install a package using apt."""
        try:
            # Update package list
            subprocess.run(
                ["sudo", "apt-get", "update"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Install the package
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", package_name],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return True
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:  # apt-get not found
            return False