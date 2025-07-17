"""
Setup script for WSJ Scrapper package.

This setup.py is provided for backwards compatibility.
The primary build configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="wsj-scrapper",
    version="0.0.1",
    author="Ariana Christodoulou",
    author_email="ariana.chr@gmail.com",
    description="A package to download articles from the Wall Street Journal via the Wayback Machine.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ariana-ch/wsj-scrapper",
    project_urls={
        "Bug Tracker": "https://github.com/ariana-ch/wsj-scrapper/issues",
        "Documentation": "https://github.com/ariana-ch/wsj-scrapper#readme",
        "Source Code": "https://github.com/ariana-ch/wsj-scrapper",
        "Changelog": "https://github.com/ariana-ch/wsj-scrapper/blob/main/CHANGELOG.md",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.9",
    install_requires=[
        "beautifulsoup4>=4.12.0",
        "pandas>=1.5.0",
        "requests>=2.28.0",
        "pydantic>=2.11.0",
        "pydantic-settings>=2.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "coverage>=7.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "coverage>=7.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    keywords="wsj news articles wayback machine web scraping financial data",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
) 