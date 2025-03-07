# sysdep/checkers/library.py
# Standard library imports
import ctypes
import glob
import json
import os
import re
import subprocess
from typing import Dict, List, Optional, Any

# Local imports
from .base import Dependency
from ..platforms import get_platform_manager

class LibraryDependency(Dependency):
    """Represents a shared library dependency."""
    
    def __init__(
        self, 
        name: str, 
        version: Optional[str] = None,
        pkg_config_name: Optional[str] = None,
        soname: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        package_names: Optional[Dict[str, str]] = None
    ):
        super().__init__(name, version, aliases)
        self.pkg_config_name = pkg_config_name or name
        self.soname = soname or f"lib{name}.so"
        # Map platform IDs to package names
        self.package_names = package_names or {}
        
    def is_installed(self) -> bool:
        """Check if the library is installed."""
        platform_system = get_platform_manager()
        
        # Try pkg-config first (works on Linux and macOS)
        if self._check_pkg_config():
            return True
            
        # Try looking for the shared object/dylib
        if self._check_shared_objects():
            return True
            
        # Platform-specific checks
        if platform_system.id == "brew":  # macOS
            return self._check_macos_specific()
        elif platform_system.id == "choco":  # Windows
            return self._check_windows_dll()
        
        return False
        
    def _check_pkg_config(self) -> bool:
        """Check if library is available via pkg-config."""
        try:
            # First check if pkg-config itself is available
            subprocess.run(
                ["pkg-config", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Then check for the library
            result = subprocess.run(
                ["pkg-config", "--exists", self.pkg_config_name],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
            
    def _check_shared_objects(self) -> bool:
        """Check if shared library files exist in standard system locations."""
        platform_system = get_platform_manager().id
        
        # Determine file extension and search paths based on platform
        if platform_system == "brew":  # macOS
            extensions = [".dylib", ".a"]
            library_prefixes = [f"lib{self.name}", f"lib{self.name.replace('-', '_')}"]
            library_paths = [
                "/usr/local/lib",
                "/usr/lib",
                "/opt/homebrew/lib",  # Apple Silicon Homebrew path
                "/opt/local/lib",     # MacPorts path
                os.path.expanduser("~/homebrew/lib"),  # Custom Homebrew installations
                os.path.expanduser("~/.homebrew/lib")
            ]
        else:  # Linux and others
            extensions = [".so", ".a"]
            library_prefixes = [f"lib{self.name}", f"lib{self.name.replace('-', '_')}"]
            library_paths = [
                "/usr/lib",
                "/usr/local/lib",
                "/lib",
                "/lib64",
                "/usr/lib64"
            ]
            
        # Check for the library with various name patterns and extensions
        for path in library_paths:
            if not os.path.exists(path):
                continue
                
            for prefix in library_prefixes:
                for ext in extensions:
                    # Check for exact matches: libname.so, libname.dylib
                    if os.path.exists(os.path.join(path, f"{prefix}{ext}")):
                        return True
                    
                    # Check for versioned libraries: libname.so.1, libname.1.dylib
                    pattern = os.path.join(path, f"{prefix}*{ext}*")
                    if glob.glob(pattern):
                        return True
                        
        return False
        
    def _check_macos_specific(self) -> bool:
        """macOS-specific library detection methods."""
        # Get package names specific to brew
        brew_pkg_name = self.package_names.get("brew", self.name)
        
        # Special case for common library mappings
        common_mappings = {
            "blas": ["openblas"],
            "lapack": ["lapack", "openblas"],  # OpenBLAS often includes LAPACK
            "opencv": ["opencv"]
        }
        
        # Check using brew if available
        try:
            # First check if the package is installed via brew
            for pkg_name in [brew_pkg_name] + common_mappings.get(self.name.lower(), []):
                try:
                    result = subprocess.run(
                        ["brew", "list", pkg_name],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    if result.returncode == 0:
                        return True
                except subprocess.CalledProcessError:
                    # Package not installed via brew, continue checking
                    pass
        except FileNotFoundError:
            # brew not found, skip this check
            pass
            
        # Check for framework directories (common for macOS system libraries)
        framework_paths = [
            "/Library/Frameworks",
            "/System/Library/Frameworks",
            os.path.expanduser("~/Library/Frameworks")
        ]
        
        for path in framework_paths:
            if os.path.exists(os.path.join(path, f"{self.name}.framework")):
                return True
                
        return False
        
    def _check_windows_dll(self) -> bool:
        """Check if DLL is available on Windows."""
        dll_name = f"{self.name}.dll"
        
        # Common DLL paths on Windows
        system_root = os.environ.get("SystemRoot", r"C:\Windows")
        dll_paths = [
            os.path.join(system_root, "System32"),
            os.path.join(system_root, "SysWOW64"),
            r"C:\Program Files",
            r"C:\Program Files (x86)"
        ]
        
        # Check if DLL exists in common paths
        for path in dll_paths:
            if os.path.exists(os.path.join(path, dll_name)):
                return True
                
        # Try loading the DLL with ctypes
        try:
            ctypes.windll.LoadLibrary(dll_name)
            return True
        except (AttributeError, OSError):
            pass
            
        return False
        
    def get_installed_version(self) -> Optional[str]:
        """Get the installed version of the library."""
        # Try pkg-config first
        try:
            result = subprocess.run(
                ["pkg-config", "--modversion", self.pkg_config_name],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        # Try platform-specific version detection
        platform = get_platform_manager()
        if platform.id == "brew":
            try:
                # Check if installed via brew
                brew_pkg_name = self.package_names.get("brew", self.name)
                result = subprocess.run(
                    ["brew", "info", "--json=v1", brew_pkg_name],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    import json
                    info = json.loads(result.stdout)
                    if info and isinstance(info, list) and len(info) > 0:
                        installed_versions = info[0].get("installed", [])
                        if installed_versions and len(installed_versions) > 0:
                            # Safely get the version from the first installed version entry
                            return installed_versions[0].get("version")
            except (subprocess.CalledProcessError, FileNotFoundError, ImportError, json.JSONDecodeError, IndexError, KeyError):
                pass
                
        # Fallback: generic version detection is challenging for libraries
        return None
        
    def get_installation_info(self) -> Dict[str, Any]:
        """Get installation information for this library."""
        platform = get_platform_manager()
        package_name = self.package_names.get(platform.id, self.name)
        
        # Special handling for macOS/brew
        if platform.id == "brew" and self.name.lower() == "blas":
            package_name = "openblas"  # Override for BLAS on macOS
            
        return {
            "name": self.name,
            "type": "library",
            "installed": self.is_installed(),
            "installed_version": self.get_installed_version(),
            "required_version": self.version,
            "package_name": package_name,
            "installation_commands": platform.get_installation_commands(package_name)
        }