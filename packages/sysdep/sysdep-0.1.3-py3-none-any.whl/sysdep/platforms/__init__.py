# sysdep/platforms/__init__.py
import sys
import platform
from typing import Optional

from .base import PlatformManager
from .linux import LinuxPlatformManager
from .macos import MacOSPlatformManager
from .windows import WindowsPlatformManager

def get_platform_manager() -> PlatformManager:
    """Get the appropriate platform manager for the current system."""
    system = platform.system().lower()
    
    if system == "linux":
        return LinuxPlatformManager()
    elif system == "darwin":
        return MacOSPlatformManager()
    elif system == "windows":
        return WindowsPlatformManager()
    else:
        raise RuntimeError(f"Unsupported platform: {system}")