# sysdep/config.py
DEFAULT_MANIFEST_FILE = "system_requirements.txt"

# Built-in dependency definitions for common tools
COMMON_DEPENDENCIES = {
    "ffmpeg": {
        "name": "ffmpeg",
        "type": "executable",
        "version_flag": "-version",
        "version_regex": r"ffmpeg version (\d+\.\d+(\.\d+)?)",
        "package_names": {
            "apt": "ffmpeg",
            "brew": "ffmpeg",
            "choco": "ffmpeg"
        }
    },
    "imagemagick": {
        "name": "convert",
        "aliases": ["magick"],
        "type": "executable",
        "version_flag": "--version",
        "version_regex": r"Version: ImageMagick (\d+\.\d+\.\d+)",
        "package_names": {
            "apt": "imagemagick",
            "brew": "imagemagick",
            "choco": "imagemagick"
        }
    },
    "opencv": {
        "name": "opencv",
        "type": "library",
        "package_names": {
            "apt": "libopencv-dev",
            "brew": "opencv",
            "choco": "opencv"
        }
    },
    "postgresql": {
        "name": "pq",
        "type": "library",
        "pkg_config_name": "libpq",
        "package_names": {
            "apt": "libpq-dev",
            "brew": "postgresql",
            "choco": "postgresql"
        }
    },
    "mysql": {
        "name": "mysqlclient",
        "type": "library",
        "package_names": {
            "apt": "libmysqlclient-dev",
            "brew": "mysql-client",
            "choco": "mysql"
        }
    },
    "sqlite": {
        "name": "sqlite3",
        "type": "library",
        "pkg_config_name": "sqlite3",
        "package_names": {
            "apt": "libsqlite3-dev",
            "brew": "sqlite",
            "choco": "sqlite"
        }
    },
    "openssl": {
        "name": "ssl",
        "type": "library",
        "pkg_config_name": "openssl",
        "package_names": {
            "apt": "libssl-dev",
            "brew": "openssl",
            "choco": "openssl"
        }
    },
    "qt5": {
        "name": "qt5",
        "type": "library",
        "pkg_config_name": "Qt5Core",
        "package_names": {
            "apt": "qt5-default",
            "brew": "qt@5",
            "choco": "qt5"
        }
    },
    "sdl2": {
        "name": "sdl2",
        "type": "library",
        "pkg_config_name": "sdl2",
        "package_names": {
            "apt": "libsdl2-dev",
            "brew": "sdl2",
            "choco": "sdl2"
        }
    },
    "cuda": {
        "name": "cudart",
        "type": "library",
        "package_names": {
            "apt": "nvidia-cuda-toolkit",
            "brew": "cuda",
            "choco": "cuda"
        }
    },
    "cudnn": {
        "name": "cudnn",
        "type": "library",
        "package_names": {
            "apt": "nvidia-cudnn",
            "brew": "cudnn",
            "choco": "cudnn"
        }
    },
    "nvidia-drivers": {
        "name": "nvidia-smi",
        "type": "executable",
        "version_flag": "--version",
        "version_regex": r"NVIDIA-SMI (\d+\.\d+(\.\d+)?)",
        "package_names": {
            "apt": "nvidia-driver-latest",
            "brew": None,
            "choco": "nvidia-display-driver"
        }
    },
    "freetype": {
        "name": "freetype",
        "type": "library",
        "pkg_config_name": "freetype2",
        "package_names": {
            "apt": "libfreetype6-dev",
            "brew": "freetype",
            "choco": "freetype"
        }
    },
    "cairo": {
        "name": "cairo",
        "type": "library",
        "pkg_config_name": "cairo",
        "package_names": {
            "apt": "libcairo2-dev",
            "brew": "cairo",
            "choco": "cairo"
        }
    },
    "gdal": {
        "name": "gdal",
        "type": "library",
        "pkg_config_name": "gdal",
        "package_names": {
            "apt": "libgdal-dev",
            "brew": "gdal",
            "choco": "gdal"
        }
    },
    "hdf5": {
        "name": "hdf5",
        "type": "library",
        "pkg_config_name": "hdf5",
        "package_names": {
            "apt": "libhdf5-dev",
            "brew": "hdf5",
            "choco": "hdf5"
        }
    }
}