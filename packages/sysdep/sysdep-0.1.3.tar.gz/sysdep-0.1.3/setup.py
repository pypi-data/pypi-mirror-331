from setuptools import setup, find_packages

setup(
    name="sysdep",
    version="0.1.3",
    description="System Dependency Checker for Python Projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Latiful Mousom",
    author_email="latifulmousom@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[ "sysdep", "dependency", "dependency-checker", "dependency-resolver", "system", "package", "verification", "installation"],
    python_requires=">=3.7",
    package_dir={"": "src"},
    packages=find_packages(where="src", include=["sysdep*"]),
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.5b2",
            "isort>=5.0.0",
            "mypy>=0.800",
            "ui",
        ],
        "ui": [
            "tqdm>=4.46.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sysdep=sysdep.cli:main",
        ],
    },
    project_urls={
        "Homepage": "https://github.com/lmousom/sysdep",
        "Issues": "https://github.com/lmousom/sysdep/issues",
    },
) 