# FlatForge Setup Guide

This guide will help you set up and run the FlatForge package on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## Installation

### Option 1: Install from GitHub

```bash
# Clone the repository
git clone https://github.com/akram0zaki/flatforge.git
cd flatforge

# Create and activate a virtual environment (recommended)
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install the package in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"

# Alternatively, install from requirements.txt
pip install -r requirements.txt
```

### Option 2: Install from PyPI (when available)

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install the package
pip install flatforge
```

## Verifying Installation

After installation, you can verify that FlatForge is working correctly:

```bash
# Run the CLI with --help to see available options
flatforge --help

# Run a simple validation test
flatforge -in examples/sample_data.txt -format examples/sample_config.yaml -verbose
```

## Running Tests

To run the test suite:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=flatforge

# Run a specific test file
pytest tests/test_utils.py
```

## Development Workflow

1. Make changes to the code
2. Run tests to ensure functionality
3. Format code with Black
   ```bash
   black flatforge
   ```
4. Run type checking with MyPy
   ```bash
   mypy flatforge
   ```
5. Run the test suite with coverage
   ```bash
   pytest --cov=flatforge
   ```

## Examples

The `examples` directory contains sample files and configurations to help you get started:

```bash
# Run an example validation
python examples/validate_file_yaml.py -in examples/sample_data.txt -format examples/sample_config.yaml
```

## Integration with FlatForgeUI

If you want to use the graphical user interface, you'll need to install the FlatForgeUI package:

```bash
pip install flatforge-ui
```

Then you can launch the configuration editor:

```bash
flatforge-config-editor
```

## Troubleshooting

If you encounter any issues:

1. Ensure you're using Python 3.8 or higher
2. Verify that all dependencies are installed correctly
3. Check that your configuration file is valid
4. Look for error messages in the console output

For more detailed information, refer to the [README.md](README.md) file. 