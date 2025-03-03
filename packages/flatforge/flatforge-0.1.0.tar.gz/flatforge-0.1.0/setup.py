"""
Setup script for FlatForge.
"""
from setuptools import setup, find_packages

setup(
    name="flatforge",
    version="0.1.0",
    description="A utility for validating and processing flat files",
    author="Akram Zaki",
    author_email="azpythonprojects@gmail.com",
    url="https://github.com/akram0zaki/flatforge",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "psutil>=5.9.0",  # For memory usage testing
        ],
        "large_files": [
            "psutil>=5.9.0",  # For monitoring memory usage with large files
        ],
        "benchmark": [
            "psutil>=5.9.0",  # For monitoring memory usage
            "matplotlib>=3.5.0",  # For creating benchmark charts
            "numpy>=1.20.0",  # Required by matplotlib
        ],
        "gui": [
            "flatforge-ui>=0.1.0",  # Optional GUI components
        ],
    },
    entry_points={
        "console_scripts": [
            "flatforge=flatforge.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)