# Installation Guide

This guide covers different ways to install the WSJ Adapter package.

## Requirements

- Python 3.9 or higher
- pip (Python package installer)

## Installation Methods

### 1. Install from Private Repository

If you have access to the private repository:

```bash
pip install wsj-adapter
```

### 2. Install from Source

#### Option A: Direct Installation from Git

```bash
pip install git+https://github.com/ariana-ch/wsj-adapter.git
```

#### Option B: Clone and Install

```bash
# Clone the repository
git clone https://github.com/ariana-ch/wsj-adapter.git
cd wsj-adapter

# Install the package
pip install .
```

#### Option C: Development Installation

For development purposes (editable installation):

```bash
# Clone the repository
git clone https://github.com/ariana-ch/wsj-adapter.git
cd wsj-adapter

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### 3. Install with Development Dependencies

If you plan to contribute to the project:

```bash
pip install -e ".[dev]"
```

This will install additional packages for testing and development:
- pytest
- black (code formatter)
- flake8 (linter)

## Virtual Environment Setup (Recommended)

It's recommended to use a virtual environment to avoid conflicts with other packages:

### Using venv (Python 3.3+)

```bash
# Create virtual environment
python -m venv wsj-adapter-env

# Activate virtual environment
# On Linux/macOS:
source wsj-adapter-env/bin/activate
# On Windows:
wsj-adapter-env\Scripts\activate

# Install the package
pip install wsj-adapter

# When done, deactivate
deactivate
```

### Using conda

```bash
# Create conda environment
conda create -n wsj-adapter python=3.9

# Activate environment
conda activate wsj-adapter

# Install the package
pip install wsj-adapter

# When done, deactivate
conda deactivate
```

## Verify Installation

To verify the installation was successful:

```python
import wsj_adapter
print(wsj_adapter.__version__)

# Test basic functionality
from wsj_adapter import WSJAdapter
import datetime

adapter = WSJAdapter(
    start_date=datetime.date(2024, 1, 1),
    end_date=datetime.date(2024, 1, 2)
)
print("WSJ Adapter initialized successfully!")
```

## System Dependencies

The package requires the following Python packages, which will be installed automatically:

- **bs4** (>=0.0.2) - HTML parsing
- **pandas** (>=1.3.0) - Data manipulation
- **requests** (>=2.32.0) - HTTP requests

## Troubleshooting

### Common Issues

#### 1. Python Version Compatibility

If you encounter version-related errors:

```bash
# Check your Python version
python --version

# Make sure it's 3.9 or higher
# If not, you may need to install a newer version of Python
```

#### 2. Permission Errors

If you get permission errors during installation:

```bash
# Try installing with user flag
pip install --user wsj-adapter

# Or use a virtual environment (recommended)
```

#### 3. Network Issues

If you have network connectivity issues:

```bash
# Try upgrading pip first
pip install --upgrade pip

# Then try installing again
pip install wsj-adapter
```

#### 4. SSL Certificate Issues

If you encounter SSL certificate errors:

```bash
# Try upgrading certificates
pip install --upgrade certifi

# Or install with trusted hosts
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org wsj-adapter
```

### Getting Help

If you encounter issues not covered here:

1. Check the [FAQ section](README.md#faq) in the README
2. Search existing [GitHub issues](https://github.com/ariana-ch/wsj-adapter/issues)
3. Create a new issue with:
   - Your operating system
   - Python version
   - Full error message
   - Steps to reproduce

## Uninstallation

To remove the package:

```bash
pip uninstall wsj-adapter
```

## Next Steps

After installation, check out:

- [README.md](README.md) for basic usage
- [examples/](examples/) for code examples
- [Contributing Guide](CONTRIBUTING.md) if you want to contribute 