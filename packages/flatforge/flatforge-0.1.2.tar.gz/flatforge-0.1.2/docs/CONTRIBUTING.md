# Contributing to FlatForge

Thank you for your interest in contributing to FlatForge! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Development Environment](#development-environment)
  - [Running Tests](#running-tests)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Coding Guidelines](#coding-guidelines)
  - [Code Style](#code-style)
  - [Documentation](#documentation)
  - [Testing](#testing)
- [Project Structure](#project-structure)
- [Release Process](#release-process)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by the FlatForge Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Development Environment

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/flatforge.git
   cd flatforge
   ```
3. Create a virtual environment and install development dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

### Running Tests

FlatForge uses pytest for testing. To run the tests:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=flatforge
```

## How to Contribute

### Reporting Bugs

If you find a bug in the code or documentation, please submit an issue to the GitHub repository. Before submitting a new issue, please check if the bug has already been reported.

When reporting a bug, please include:

- A clear and descriptive title.
- A detailed description of the issue, including steps to reproduce.
- The expected behavior and what actually happened.
- Any relevant logs or error messages.
- Your environment (OS, Python version, etc.).

### Suggesting Enhancements

If you have an idea for an enhancement or a new feature, please submit an issue to the GitHub repository. Before submitting a new issue, please check if the enhancement has already been suggested.

When suggesting an enhancement, please include:

- A clear and descriptive title.
- A detailed description of the proposed enhancement.
- Any relevant examples or use cases.
- If applicable, any potential implementation details.

### Pull Requests

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
   or
   ```bash
   git checkout -b fix/your-bugfix-name
   ```

2. Make your changes and commit them with a descriptive commit message:
   ```bash
   git commit -m "Add feature: your feature description"
   ```
   or
   ```bash
   git commit -m "Fix: your bugfix description"
   ```

3. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Submit a pull request to the main repository.

5. The maintainers will review your pull request and may request changes or provide feedback.

## Coding Guidelines

### Code Style

FlatForge follows the PEP 8 style guide for Python code. We use Black for code formatting and flake8 for linting.

To format your code:

```bash
black flatforge tests
```

To check for linting issues:

```bash
flake8 flatforge tests
```

### Documentation

- All public modules, classes, methods, and functions should have docstrings.
- Use Google-style docstrings.
- Keep the documentation up-to-date with the code.

Example:

```python
def function(arg1, arg2):
    """Summary of function.
    
    Longer description of function.
    
    Args:
        arg1: Description of arg1.
        arg2: Description of arg2.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: Description of when this error is raised.
    """
    pass
```

### Testing

- Write tests for all new features and bugfixes.
- Aim for high test coverage.
- Tests should be clear, concise, and focused on a single functionality.

## Project Structure

The FlatForge project is structured as follows:

```
flatforge/
├── docs/                 # Documentation
├── examples/             # Example code and configurations
├── flatforge/            # Main package
│   ├── __init__.py       # Package initialization
│   ├── cli.py            # Command-line interface
│   ├── config_parser.py  # Configuration parsing
│   ├── models.py         # Data models
│   ├── processor.py      # File processing
│   ├── validators.py     # Validation rules
│   └── ...               # Other modules
├── tests/                # Test suite
├── .gitignore            # Git ignore file
├── LICENSE               # License file
├── pyproject.toml        # Project configuration
├── README.md             # Project readme
└── setup.py              # Setup script
```

## Release Process

1. Update the version number in `setup.py` and `pyproject.toml`.
2. Update the changelog with the new version and its changes.
3. Create a new release on GitHub with the version number as the tag.
4. The CI/CD pipeline will automatically publish the new version to PyPI.

## Community

- Join the discussion on GitHub issues and pull requests.
- Follow the project on GitHub to stay updated on new releases and changes.
- Share your experience with FlatForge and help others in the community.

Thank you for contributing to FlatForge! 