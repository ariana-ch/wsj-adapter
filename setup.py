"""
Setup script for WSJ Adapter package.

This setup.py is provided for backwards compatibility.
The primary build configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="wsj-adapter",
    version="0.0.1",
    author="Ariana Christodoulou",
    author_email="ariana.chr@gmail.com",
    description="A package to download articles from the Wall Street Journal via the Wayback Machine.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ariana-ch/wsj-adapter",
    project_urls={
        "Bug Tracker": "https://github.com/ariana-ch/wsj-adapter/issues",
        "Documentation": "https://github.com/ariana-ch/wsj-adapter",
        "Source Code": "https://github.com/ariana-ch/wsj-adapter",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.9",
    install_requires=[
        "bs4>=0.0.2",
        "pandas>=1.3.0",
        "requests>=2.32.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    keywords="wsj news articles wayback machine",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
) 