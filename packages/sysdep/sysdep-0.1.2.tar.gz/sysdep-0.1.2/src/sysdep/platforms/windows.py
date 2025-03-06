# sysdep/platforms/windows.py
import os
import subprocess
from typing import Dict, List, Optional

from .base import PlatformManager

class WindowsPlatformManager(PlatformManager):
    """Platform manager for Windows systems."""
    
    @property
    def id(self) -> str:
        return "choco"  # Using Chocolatey as the default package manager
        
    def is_current_platform(self) -> bool:
        import platform
        return platform.system().lower() == "windows"
        
    def get_installation_commands(self, package_name: str) -> List[str]:
        return [
            f"choco install {package_name} -y"
        ]
        
    def install_package(self, package_name: str) -> bool:
        """Install a package using Chocolatey."""
        try:
            # Check if Chocolatey is installed
            if not self._check_choco_installed():
                return False
                
            # Install the package
            # Using shell=True because on Windows, Chocolatey is often a batch file
            subprocess.run(
                f"choco install {package_name} -y",
                check=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return True
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return False
            
    def _check_choco_installed(self) -> bool:
        """Check if Chocolatey is installed."""
        try:
            subprocess.run(
                ["choco", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
            
    def get_package_manager_installation_instructions(self) -> str:
        """Get instructions for installing Chocolatey."""
        return """
        To install Chocolatey, run the following command in an Administrator PowerShell:
        
        Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        """