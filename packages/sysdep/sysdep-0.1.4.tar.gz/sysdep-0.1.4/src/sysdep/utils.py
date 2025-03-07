# sysdep/utils.py
# Standard library imports
import os
import sys
import subprocess
import textwrap
from typing import Dict, List, Any, Optional, Set, Iterable, TypeVar, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count

# Try to import tqdm for progress bars, gracefully fallback if not available
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Local imports
from .platforms import get_platform_manager
from .checkers.base import Dependency

# Type variable for generic functions
T = TypeVar('T')
R = TypeVar('R')

# Default number of worker threads (use CPU count but cap at 8)
DEFAULT_WORKERS = min(8, cpu_count())

def parallel_map(func: Callable[[T], R], 
                items: Iterable[T], 
                desc: str = "Processing",
                show_progress: bool = True,
                max_workers: Optional[int] = None) -> List[R]:
    """
    Execute a function over an iterable in parallel with progress bar.
    
    Args:
        func: Function to execute for each item
        items: Iterable of items to process
        desc: Description for the progress bar
        show_progress: Whether to show a progress bar
        max_workers: Maximum number of worker threads (defaults to min(8, CPU count))
        
    Returns:
        List of results in the same order as the input items
    """
    items = list(items)  # Convert to list to get length and ensure single iteration
    if not items:
        return []
        
    max_workers = max_workers or DEFAULT_WORKERS
    
    # For small numbers of items, don't bother with parallelization
    if len(items) < 2:
        results = [func(item) for item in items]
        return results
        
    # Use ThreadPoolExecutor for parallelization
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(func, item): i for i, item in enumerate(items)}
        
        # Setup progress bar if enabled
        if TQDM_AVAILABLE and show_progress:
            pbar = tqdm(total=len(items), desc=desc)
        
        # Collect results while maintaining input order
        results = [None] * len(items)
        try:
            for future in as_completed(futures):
                index = futures[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    print(f"Error processing item {index}: {e}", file=sys.stderr)
                    results[index] = None
                
                if TQDM_AVAILABLE and show_progress:
                    pbar.update(1)
        finally:
            if TQDM_AVAILABLE and show_progress:
                pbar.close()
                
    return results

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def with_progress(iterable: Iterable[T], desc: str = "Processing", disable: bool = False) -> Iterable[T]:
    """
    Wrap an iterable with a progress bar if tqdm is available.
    
    Args:
        iterable: The iterable to process
        desc: Description for the progress bar
        disable: Whether to disable the progress bar
        
    Returns:
        The original iterable wrapped with a progress bar if tqdm is available,
        otherwise returns the original iterable
    """
    if TQDM_AVAILABLE and not disable:
        return tqdm(iterable, desc=desc)
    return iterable

def progress_task(total: int, desc: str = "Processing", disable: bool = False):
    """
    Create a progress bar context manager for tasks without an iterable.
    
    Args:
        total: Total number of steps
        desc: Description for the progress bar
        disable: Whether to disable the progress bar
        
    Returns:
        A progress bar context manager if tqdm is available, otherwise a dummy context manager
    """
    if TQDM_AVAILABLE and not disable:
        return tqdm(total=total, desc=desc)
    
    # Dummy context manager if tqdm is not available
    class DummyProgress:
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        
        def update(self, n=1):
            pass
        
        def set_description(self, desc):
            pass
    
    return DummyProgress()

def print_dependency_report(results: Dict[str, Any]):
    """Print a human-readable dependency report."""
    total = len(results["dependencies"])
    missing = len(results["missing"])
    installed = total - missing
    
    # Print header
    print(f"\n  {Colors.BOLD}{Colors.CYAN}⚡ sysdep{Colors.ENDC} {Colors.HEADER}v1.0{Colors.ENDC}")
    print(f"  {Colors.BOLD}Scanning dependencies...{Colors.ENDC}\n")
    
    # Print summary with modern bullet points
    print(f"  {Colors.BOLD}Status{Colors.ENDC}")
    print(f"    {Colors.CYAN}◆{Colors.ENDC} Dependencies found: {Colors.BOLD}{total}{Colors.ENDC}")
    print(f"    {Colors.GREEN}◆{Colors.ENDC} Successfully installed: {Colors.BOLD}{installed}{Colors.ENDC}")
    print(f"    {Colors.RED if missing > 0 else Colors.GREEN}◆{Colors.ENDC} Missing: {Colors.BOLD}{missing}{Colors.ENDC}\n")
    
    if missing > 0:
        print(f"  {Colors.BOLD}{Colors.RED}Missing Dependencies{Colors.ENDC}")
        platform = get_platform_manager()
        
        for i, dep in enumerate(results["missing"], 1):
            print(f"\n    {Colors.YELLOW}▲ {dep['name']}{Colors.ENDC}")
            if dep.get('required_version'):
                print(f"      Required version: {Colors.CYAN}{dep['required_version']}{Colors.ENDC}")
            
            # Print installation commands
            print(f"\n      {Colors.BOLD}Run:{Colors.ENDC}")
            for cmd in dep["installation_commands"]:
                print(f"      $ {Colors.GREEN}{cmd}{Colors.ENDC}")
            print()
    else:
        print(f"  {Colors.BOLD}{Colors.GREEN}✓ All dependencies are installed!{Colors.ENDC}\n")

def install_dependencies(dependencies: List[Dict[str, Any]], show_progress: bool = True, max_workers: Optional[int] = None) -> bool:
    """
    Install missing dependencies.
    
    Args:
        dependencies: List of dependency info dictionaries
        show_progress: Whether to show a progress bar during installation
        max_workers: Maximum number of worker threads for parallel processing (not used for installation)
        
    Returns:
        bool: True if all dependencies were installed, False otherwise
    """
    platform = get_platform_manager()
    all_success = True
    os_id = get_os_identifier()
    
    # Special case handling for NVIDIA packages
    nvidia_deps = [dep for dep in dependencies if _is_nvidia_package(dep['name'])]
    other_deps = [dep for dep in dependencies if not _is_nvidia_package(dep['name'])]
    
    if nvidia_deps:
        print(f"\n{Colors.BOLD}NVIDIA Dependencies{Colors.ENDC}")
        print("These packages require special installation steps:\n")
        
        if os_id == 'darwin':
            print(f"{Colors.YELLOW}Note: NVIDIA CUDA is not supported on newer macOS versions.{Colors.ENDC}")
            print("If you're using an Intel Mac, please follow these steps:\n")
            print("1. Download CUDA Toolkit from NVIDIA website:")
            print("   https://developer.nvidia.com/cuda-downloads\n")
            print("2. Download cuDNN from NVIDIA Developer site (requires free registration):")
            print("   https://developer.nvidia.com/cudnn\n")
            print(f"{Colors.BOLD}For Apple Silicon Macs:{Colors.ENDC}")
            print("Consider using alternatives like Apple's Metal Performance Shaders (MPS)\n")
        
        elif os_id == 'linux':
            print("Follow these steps to install NVIDIA packages:\n")
            print("1. Add NVIDIA package repository:")
            print(f"   {Colors.GREEN}$ wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb{Colors.ENDC}")
            print(f"   {Colors.GREEN}$ sudo dpkg -i cuda-keyring_1.0-1_all.deb{Colors.ENDC}")
            print(f"   {Colors.GREEN}$ sudo apt-get update{Colors.ENDC}\n")
            print("2. Install CUDA Toolkit:")
            print(f"   {Colors.GREEN}$ sudo apt-get install cuda{Colors.ENDC}\n")
            print("3. Install cuDNN (requires NVIDIA Developer account):")
            print("   Download from: https://developer.nvidia.com/cudnn\n")
            print("4. Add to your environment:")
            print(f"   {Colors.GREEN}$ echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc{Colors.ENDC}")
            print(f"   {Colors.GREEN}$ echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc{Colors.ENDC}\n")
        
        elif os_id == 'windows':
            print("Follow these steps to install NVIDIA packages:\n")
            print("1. Download and install CUDA Toolkit:")
            print("   https://developer.nvidia.com/cuda-downloads\n")
            print("2. Download and install cuDNN (requires NVIDIA Developer account):")
            print("   https://developer.nvidia.com/cudnn\n")
            print("3. Add CUDA paths to your system environment variables\n")
        
        print(f"{Colors.YELLOW}Note: After installation, you may need to restart your system.{Colors.ENDC}\n")
        all_success = False
    
    # Install other dependencies normally
    if other_deps:
        print(f"\n{Colors.BOLD}Installing other dependencies...{Colors.ENDC}")
        for dep in with_progress(other_deps, desc="Installing dependencies", disable=not show_progress):
            print(f"\n  {Colors.BOLD}Installing {Colors.CYAN}{dep['name']}{Colors.ENDC}...")
            
            success = platform.install_package(dep["package_name"])
            if success:
                print(f"    {Colors.GREEN}✓{Colors.ENDC} {dep['name']} installed successfully")
            else:
                all_success = False
                print(f"    {Colors.RED}✗{Colors.ENDC} Failed to install {dep['name']}")
                print(f"\n    {Colors.BOLD}Manual installation commands:{Colors.ENDC}")
                for cmd in dep["installation_commands"]:
                    print(f"    $ {Colors.GREEN}{cmd}{Colors.ENDC}")
            print()
    
    return all_success

def _is_nvidia_package(name: str) -> bool:
    """Check if a package is NVIDIA-related."""
    nvidia_packages = {
        'nvidia-smi', 'cudart', 'cudnn', 'cuda', 'nvidia-cuda',
        'nvidia-driver', 'nvidia-toolkit', 'cuda-toolkit'
    }
    return name.lower() in nvidia_packages or 'cuda' in name.lower() or 'nvidia' in name.lower()

def check_package_manager_installed() -> bool:
    """Check if the current platform's package manager is installed."""
    platform = get_platform_manager()
    
    # For Linux/apt
    if platform.id == "apt":
        try:
            subprocess.run(
                ["apt-get", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    # For macOS/brew
    elif platform.id == "brew":
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
    
    # For Windows/choco
    elif platform.id == "choco":
        try:
            # On Windows, Chocolatey is often a batch file
            subprocess.run(
                "choco --version",
                check=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    return False

def get_package_manager_installation_instructions() -> str:
    """Get installation instructions for the current platform's package manager."""
    platform = get_platform_manager()
    
    # For Linux/apt (should be preinstalled)
    if platform.id == "apt":
        return "The apt package manager should already be installed on your Debian/Ubuntu system."
    
    # For macOS/brew
    elif platform.id == "brew":
        return textwrap.dedent("""
        To install Homebrew on macOS, run:
        
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        """)
    
    # For Windows/choco
    elif platform.id == "choco":
        return textwrap.dedent("""
        To install Chocolatey on Windows, run the following command in an Administrator PowerShell:
        
        Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        """)
    
    return "Unknown platform. Please install a package manager appropriate for your system."

def get_os_identifier() -> str:
    """
    Get a simple OS identifier string.
    
    Returns:
        'linux', 'darwin', 'windows', or 'unknown'
    """
    import platform
    system = platform.system().lower()
    
    if system == 'linux':
        return 'linux'
    elif system == 'darwin':
        return 'darwin'
    elif system == 'windows':
        return 'windows'
    else:
        return 'unknown'