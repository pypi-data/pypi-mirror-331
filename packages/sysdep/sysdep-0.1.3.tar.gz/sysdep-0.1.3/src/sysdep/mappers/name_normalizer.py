# sysdep/mappers/name_normalizer.py
"""Package name normalization utilities."""

# Mapping for package name normalization (handles different naming schemes)
PACKAGE_NAME_NORMALIZATION = {
    # OpenCV variations
    'opencv-python-headless': 'opencv-python',
    'opencv-contrib-python': 'opencv-python',
    'opencv-contrib-python-headless': 'opencv-python',
    'opencv': 'opencv-python',
    
    # Pillow and PIL
    'pillow-simd': 'pillow',
    'pil': 'pillow',
    'python-pillow': 'pillow',
    
    # Database drivers
    'mysql-python': 'mysqlclient',
    'mysqldb': 'mysqlclient',
    'psycopg': 'psycopg2',
    'psycopg2-binary': 'psycopg2',
    
    # XML processing
    'python-lxml': 'lxml',
    
    # Machine learning
    'tensorflow-gpu': 'tensorflow',
    'tensorflow-cpu': 'tensorflow',
    'tf': 'tensorflow',
    'torch': 'pytorch',
    'pytorch-gpu': 'pytorch',
    'pytorch-cpu': 'pytorch',
    'sklearn': 'scikit-learn',
    'scikit_learn': 'scikit-learn',
    
    # Scientific
    'np': 'numpy',
    'pd': 'pandas',
    'matplotlib.pyplot': 'matplotlib',
    'mpl': 'matplotlib',
    
    # GUI
    'qt5': 'pyqt5',
    'pyside': 'pyside2',
    'qt': 'pyqt5',
    'wx': 'wxpython',
    
    # Database ORM
    'sqlalchemy-orm': 'sqlalchemy',
    'sql-alchemy': 'sqlalchemy',
    
    # Networking
    'zeromq': 'pyzmq',
    'zmq': 'pyzmq',
    'mqtt': 'paho-mqtt',
    
    # Web
    'bs4': 'beautifulsoup4',
    'beautifulsoup': 'beautifulsoup4',
    'django-rest-framework': 'django',
    'djangorestframework': 'django',
    
    # Document processing
    'pdfkit': 'wkhtmltopdf',
    'pdf': 'reportlab',
}

def normalize_package_name(package_name: str) -> str:
    """
    Normalize package name to match our mapping.
    
    Args:
        package_name: The package name to normalize
        
    Returns:
        The normalized package name
    """
    # Remove version specifier if present
    package_name = package_name.split('==')[0].split('>=')[0].split('>')[0].split('<')[0].strip()
    # Convert to lowercase
    package_name = package_name.lower()
    # Use normalization map if available
    return PACKAGE_NAME_NORMALIZATION.get(package_name, package_name) 