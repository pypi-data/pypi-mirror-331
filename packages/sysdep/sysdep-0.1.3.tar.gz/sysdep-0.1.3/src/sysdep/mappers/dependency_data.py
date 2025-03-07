# sysdep/mappers/dependency_data.py
"""Package dependency mappings for system dependencies."""

# Local imports
from ..checkers.executable import ExecutableDependency
from ..checkers.library import LibraryDependency

# Mapping from Python package names to system dependencies
# Format: 'package_name': [list of system dependency objects]
PACKAGE_DEPENDENCIES = {
    # Image processing
    'pillow': [
        LibraryDependency(
            name='jpeg', 
            pkg_config_name='libjpeg',
            package_names={'apt': 'libjpeg-dev', 'brew': 'jpeg', 'choco': 'libjpeg-turbo'}
        ),
        LibraryDependency(
            name='png', 
            pkg_config_name='libpng',
            package_names={'apt': 'libpng-dev', 'brew': 'libpng', 'choco': 'libpng'}
        ),
        LibraryDependency(
            name='tiff',
            pkg_config_name='libtiff-4',
            package_names={'apt': 'libtiff5-dev', 'brew': 'libtiff', 'choco': 'libtiff'}
        ),
        LibraryDependency(
            name='freetype',
            pkg_config_name='freetype2',
            package_names={'apt': 'libfreetype6-dev', 'brew': 'freetype', 'choco': 'freetype'}
        ),
    ],
    'opencv-python': [
        LibraryDependency(
            name='opencv', 
            package_names={'apt': 'libopencv-dev', 'brew': 'opencv', 'choco': 'opencv'}
        ),
    ],
    'scikit-image': [
        LibraryDependency(
            name='fftw',
            pkg_config_name='fftw3',
            package_names={'apt': 'libfftw3-dev', 'brew': 'fftw', 'choco': 'fftw'}
        ),
    ],
    
    # Audio/video processing
    'moviepy': [
        ExecutableDependency(
            name='ffmpeg',
            package_names={'apt': 'ffmpeg', 'brew': 'ffmpeg', 'choco': 'ffmpeg'}
        ),
    ],
    'pydub': [
        ExecutableDependency(
            name='ffmpeg',
            package_names={'apt': 'ffmpeg', 'brew': 'ffmpeg', 'choco': 'ffmpeg'}
        ),
    ],
    'librosa': [
        LibraryDependency(
            name='sndfile',
            pkg_config_name='sndfile',
            package_names={'apt': 'libsndfile1-dev', 'brew': 'libsndfile', 'choco': 'libsndfile'}
        ),
        ExecutableDependency(
            name='ffmpeg',
            package_names={'apt': 'ffmpeg', 'brew': 'ffmpeg', 'choco': 'ffmpeg'}
        ),
    ],
    'pyaudio': [
        LibraryDependency(
            name='portaudio',
            pkg_config_name='portaudio-2.0',
            package_names={'apt': 'portaudio19-dev', 'brew': 'portaudio', 'choco': 'portaudio'}
        ),
    ],
    
    # Scientific computing
    'numpy': [
        LibraryDependency(
            name='lapack',
            package_names={'apt': 'liblapack-dev', 'brew': 'lapack', 'choco': 'lapack'}
        ),
        LibraryDependency(
            name='blas',
            package_names={'apt': 'libblas-dev', 'brew': 'openblas', 'choco': 'openblas'}
        ),
    ],
    'scipy': [
        LibraryDependency(
            name='lapack',
            package_names={'apt': 'liblapack-dev', 'brew': 'lapack', 'choco': 'lapack'}
        ),
        LibraryDependency(
            name='blas',
            package_names={'apt': 'libblas-dev', 'brew': 'openblas', 'choco': 'openblas'}
        ),
        LibraryDependency(
            name='fftw',
            pkg_config_name='fftw3',
            package_names={'apt': 'libfftw3-dev', 'brew': 'fftw', 'choco': 'fftw'}
        ),
    ],
    'pandas': [
        LibraryDependency(
            name='blas',
            package_names={'apt': 'libblas-dev', 'brew': 'openblas', 'choco': 'openblas'}
        ),
    ],
    'statsmodels': [
        LibraryDependency(
            name='blas',
            package_names={'apt': 'libblas-dev', 'brew': 'openblas', 'choco': 'openblas'}
        ),
    ],
    'sympy': [],  # Pure Python, no system dependencies
    
    # Database connectors
    'psycopg2': [
        LibraryDependency(
            name='pq',
            pkg_config_name='libpq',
            package_names={'apt': 'libpq-dev', 'brew': 'postgresql', 'choco': 'postgresql'}
        ),
    ],
    'mysqlclient': [
        LibraryDependency(
            name='mysqlclient',
            package_names={'apt': 'libmysqlclient-dev', 'brew': 'mysql-client', 'choco': 'mysql'}
        ),
    ],
    'pymongo': [],  # No system dependencies
    'sqlite3': [
        LibraryDependency(
            name='sqlite3',
            pkg_config_name='sqlite3',
            package_names={'apt': 'libsqlite3-dev', 'brew': 'sqlite', 'choco': 'sqlite'}
        ),
    ],
    'sqlalchemy': [],  # Python ORM, dependencies depend on the database used
    
    # Web/Network
    'lxml': [
        LibraryDependency(
            name='xml2',
            pkg_config_name='libxml-2.0',
            package_names={'apt': 'libxml2-dev', 'brew': 'libxml2', 'choco': 'libxml2'}
        ),
        LibraryDependency(
            name='xslt',
            pkg_config_name='libxslt',
            package_names={'apt': 'libxslt1-dev', 'brew': 'libxslt', 'choco': 'libxslt'}
        ),
    ],
    'requests': [],  # Pure Python, no system dependencies
    'aiohttp': [],   # Mostly Python, no significant system dependencies
    'flask': [],     # Pure Python web framework
    'django': [],    # Pure Python web framework
    'fastapi': [],   # Pure Python web framework
    'beautifulsoup4': [],  # Pure Python HTML parser
    'scrapy': [
        LibraryDependency(
            name='jpeg', 
            pkg_config_name='libjpeg',
            package_names={'apt': 'libjpeg-dev', 'brew': 'jpeg', 'choco': 'libjpeg-turbo'}
        ),
    ],
    'cryptography': [
        LibraryDependency(
            name='ssl',
            pkg_config_name='openssl',
            package_names={'apt': 'libssl-dev', 'brew': 'openssl', 'choco': 'openssl'}
        ),
        LibraryDependency(
            name='crypto',
            pkg_config_name='libcrypto',
            package_names={'apt': 'libssl-dev', 'brew': 'openssl', 'choco': 'openssl'}
        ),
    ],
    'pycrypto': [
        LibraryDependency(
            name='gmp',
            pkg_config_name='gmp',
            package_names={'apt': 'libgmp-dev', 'brew': 'gmp', 'choco': 'gmp'}
        ),
    ],
    
    # Graphics and GUI
    'matplotlib': [
        LibraryDependency(
            name='freetype',
            pkg_config_name='freetype2',
            package_names={'apt': 'libfreetype6-dev', 'brew': 'freetype', 'choco': 'freetype'}
        ),
        LibraryDependency(
            name='png',
            pkg_config_name='libpng',
            package_names={'apt': 'libpng-dev', 'brew': 'libpng', 'choco': 'libpng'}
        ),
    ],
    'pycairo': [
        LibraryDependency(
            name='cairo',
            pkg_config_name='cairo',
            package_names={'apt': 'libcairo2-dev', 'brew': 'cairo', 'choco': 'cairo'}
        ),
    ],
    'pygobject': [
        LibraryDependency(
            name='gobject',
            pkg_config_name='gobject-2.0',
            package_names={'apt': 'libgirepository1.0-dev', 'brew': 'gobject-introspection', 'choco': 'gobject-introspection'}
        ),
    ],
    'pyqt5': [
        LibraryDependency(
            name='qt5',
            pkg_config_name='Qt5Core',
            package_names={'apt': 'qt5-default', 'brew': 'qt@5', 'choco': 'qt5'}
        ),
    ],
    'pyside2': [
        LibraryDependency(
            name='qt5',
            pkg_config_name='Qt5Core',
            package_names={'apt': 'qt5-default', 'brew': 'qt@5', 'choco': 'qt5'}
        ),
    ],
    'wxpython': [
        LibraryDependency(
            name='wx',
            pkg_config_name='wx-3.0',
            package_names={'apt': 'libwxgtk3.0-dev', 'brew': 'wxwidgets', 'choco': 'wxwidgets'}
        ),
    ],
    'kivy': [
        LibraryDependency(
            name='sdl2',
            pkg_config_name='sdl2',
            package_names={'apt': 'libsdl2-dev', 'brew': 'sdl2', 'choco': 'sdl2'}
        ),
        LibraryDependency(
            name='glew',
            pkg_config_name='glew',
            package_names={'apt': 'libglew-dev', 'brew': 'glew', 'choco': 'glew'}
        ),
    ],
    
    # Machine learning
    'tensorflow': [
        ExecutableDependency(
            name='nvidia-smi',
            package_names={'apt': 'nvidia-driver-latest', 'brew': None, 'choco': 'nvidia-display-driver'}
        ),
        LibraryDependency(
            name='cudart',
            package_names={'apt': 'nvidia-cuda-toolkit', 'brew': 'cuda', 'choco': 'cuda'}
        ),
        LibraryDependency(
            name='cudnn',
            package_names={'apt': 'nvidia-cudnn', 'brew': 'cudnn', 'choco': 'cudnn'}
        ),
    ],
    'pytorch': [
        ExecutableDependency(
            name='nvidia-smi',
            package_names={'apt': 'nvidia-driver-latest', 'brew': None, 'choco': 'nvidia-display-driver'}
        ),
        LibraryDependency(
            name='cudart',
            package_names={'apt': 'nvidia-cuda-toolkit', 'brew': 'cuda', 'choco': 'cuda'}
        ),
        LibraryDependency(
            name='cudnn',
            package_names={'apt': 'nvidia-cudnn', 'brew': 'cudnn', 'choco': 'cudnn'}
        ),
    ],
    'scikit-learn': [
        LibraryDependency(
            name='blas',
            package_names={'apt': 'libblas-dev', 'brew': 'openblas', 'choco': 'openblas'}
        ),
    ],
    'xgboost': [
        LibraryDependency(
            name='blas',
            package_names={'apt': 'libblas-dev', 'brew': 'openblas', 'choco': 'openblas'}
        ),
    ],
    'lightgbm': [
        LibraryDependency(
            name='openmp',
            package_names={'apt': 'libomp-dev', 'brew': 'libomp', 'choco': 'llvm'}
        ),
    ],
    
    # Document processing
    'wkhtmltopdf': [
        ExecutableDependency(
            name='wkhtmltopdf',
            package_names={'apt': 'wkhtmltopdf', 'brew': 'wkhtmltopdf', 'choco': 'wkhtmltopdf'}
        ),
    ],
    'weasyprint': [
        LibraryDependency(
            name='pango',
            pkg_config_name='pango',
            package_names={'apt': 'libpango1.0-dev', 'brew': 'pango', 'choco': 'pango'}
        ),
        LibraryDependency(
            name='cairo',
            pkg_config_name='cairo',
            package_names={'apt': 'libcairo2-dev', 'brew': 'cairo', 'choco': 'cairo'}
        ),
    ],
    'reportlab': [
        LibraryDependency(
            name='freetype',
            pkg_config_name='freetype2',
            package_names={'apt': 'libfreetype6-dev', 'brew': 'freetype', 'choco': 'freetype'}
        ),
    ],
    'pypdf2': [],  # Pure Python PDF manipulation
    
    # Data serialization
    'pyyaml': [
        LibraryDependency(
            name='yaml',
            pkg_config_name='yaml-0.1',
            package_names={'apt': 'libyaml-dev', 'brew': 'libyaml', 'choco': 'libyaml'}
        ),
    ],
    
    # Networking & Communication
    'twisted': [],  # Pure Python
    'paramiko': [],  # Pure Python SSH implementation
    'netcdf4': [
        LibraryDependency(
            name='netcdf',
            pkg_config_name='netcdf',
            package_names={'apt': 'libnetcdf-dev', 'brew': 'netcdf', 'choco': 'netcdf'}
        ),
        LibraryDependency(
            name='hdf5',
            pkg_config_name='hdf5',
            package_names={'apt': 'libhdf5-dev', 'brew': 'hdf5', 'choco': 'hdf5'}
        ),
    ],
    'h5py': [
        LibraryDependency(
            name='hdf5',
            pkg_config_name='hdf5',
            package_names={'apt': 'libhdf5-dev', 'brew': 'hdf5', 'choco': 'hdf5'}
        ),
    ],
    'pyzmq': [
        LibraryDependency(
            name='zmq',
            pkg_config_name='libzmq',
            package_names={'apt': 'libzmq3-dev', 'brew': 'zeromq', 'choco': 'zeromq'}
        ),
    ],
    'paho-mqtt': [],  # Pure Python MQTT client
    
    # Geographic Information Systems
    'gdal': [
        LibraryDependency(
            name='gdal',
            pkg_config_name='gdal',
            package_names={'apt': 'libgdal-dev', 'brew': 'gdal', 'choco': 'gdal'}
        ),
    ],
    'fiona': [
        LibraryDependency(
            name='gdal',
            pkg_config_name='gdal',
            package_names={'apt': 'libgdal-dev', 'brew': 'gdal', 'choco': 'gdal'}
        ),
    ],
    'rasterio': [
        LibraryDependency(
            name='gdal',
            pkg_config_name='gdal',
            package_names={'apt': 'libgdal-dev', 'brew': 'gdal', 'choco': 'gdal'}
        ),
    ],
    'shapely': [
        LibraryDependency(
            name='geos',
            pkg_config_name='geos',
            package_names={'apt': 'libgeos-dev', 'brew': 'geos', 'choco': 'geos'}
        ),
    ],
    'pyproj': [
        LibraryDependency(
            name='proj',
            pkg_config_name='proj',
            package_names={'apt': 'libproj-dev', 'brew': 'proj', 'choco': 'proj'}
        ),
    ],
    
    # Compression
    'python-snappy': [
        LibraryDependency(
            name='snappy',
            package_names={'apt': 'libsnappy-dev', 'brew': 'snappy', 'choco': 'snappy'}
        ),
    ],
    'python-lzo': [
        LibraryDependency(
            name='lzo',
            pkg_config_name='lzo2',
            package_names={'apt': 'liblzo2-dev', 'brew': 'lzo', 'choco': 'lzo'}
        ),
    ],
    'lz4': [
        LibraryDependency(
            name='lz4',
            pkg_config_name='liblz4',
            package_names={'apt': 'liblz4-dev', 'brew': 'lz4', 'choco': 'lz4'}
        ),
    ],
    
    # Game development
    'pygame': [
        LibraryDependency(
            name='sdl2',
            pkg_config_name='sdl2',
            package_names={'apt': 'libsdl2-dev', 'brew': 'sdl2', 'choco': 'sdl2'}
        ),
        LibraryDependency(
            name='sdl2_mixer',
            pkg_config_name='SDL2_mixer',
            package_names={'apt': 'libsdl2-mixer-dev', 'brew': 'sdl2_mixer', 'choco': 'sdl2_mixer'}
        ),
    ],
    'pyglet': [
        LibraryDependency(
            name='glew',
            pkg_config_name='glew',
            package_names={'apt': 'libglew-dev', 'brew': 'glew', 'choco': 'glew'}
        ),
    ],
    'pyopengl': [
        LibraryDependency(
            name='gl',
            package_names={'apt': 'libgl1-mesa-dev', 'brew': None, 'choco': None}  # Usually provided by graphics drivers
        ),
    ],
} 