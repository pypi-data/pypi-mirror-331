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
    # Add more common dependencies here for non python dependencies
    
    
}