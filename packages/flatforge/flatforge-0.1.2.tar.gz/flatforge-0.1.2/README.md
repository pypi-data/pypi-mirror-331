# FlatForge

FlatForge is a Python library for processing and validating flat files (fixed-length or delimited) with a focus on flexibility and ease of use.

**GitHub Repository**: [https://github.com/akram0zaki/flatforge](https://github.com/akram0zaki/flatforge)

## Features

- Support for fixed-length and delimited file formats
- Configurable validation rules for individual fields
- Global validation rules across multiple records
- Detailed error reporting
- YAML and string-based configuration options
- Extensible architecture for custom validators and processors

## Installation

```bash
pip install flatforge
```

## Quick Start

```python
from flatforge.config_parser import StringConfigParser
from flatforge.processor import Processor

# Create a configuration
config = """
[parameters]
delimiter = ,
section_separator = \n\n
record_separator = \n

[section_metadata]
0 = fl{10,5,15}|0:required,numeric|1:length(5)|2:regex([A-Z]{2,})
"""

# Parse the configuration
parser = StringConfigParser()
file_props = parser.parse(config)

# Create a processor
processor = Processor(file_props)

# Process a file
file_content = "1234567890ABCDE               \n0987654321FGHIJ               "
results = processor.process_file(file_content)

# Check for errors
for section_index, section_results in results.items():
    for result in section_results:
        if not result.is_valid:
            print(f"Error in section {section_index}, column {result.message.column_index}: {result.message.text}")
```

## Documentation

For comprehensive documentation, see the [docs](docs/) directory:

- [User Guide](docs/user_guide.md) - A guide to using FlatForge, including installation, basic usage, and advanced features.
- [API Reference](docs/api_reference.md) - A comprehensive reference for the FlatForge API.
- [Architecture](docs/design/architecture.md) - Detailed information about the architecture, design patterns, and extensibility of FlatForge.

## Core Concepts

### FileProperties

The `FileProperties` class represents the structure and validation rules for a flat file. It contains:

- **Parameters**: General settings like delimiters and separators
- **Sections**: Different parts of the file, each with its own format and rules
- **Global Rules**: Rules that apply across multiple records

### Rule

A `Rule` defines a validation check for a specific field. Rules can be:

- **Basic Rules**: Apply to individual fields (e.g., required, length, regex)
- **Global Rules**: Apply across multiple records (e.g., uniqueness, sums)

### Processor

The `Processor` applies the rules defined in a `FileProperties` object to validate file content.

## Configuration

FlatForge supports both string-based and YAML-based configuration.

### String Configuration

```
[parameters]
delimiter = ,
section_separator = \n\n
record_separator = \n

[section_metadata]
0 = fl{10,5,15}|0:required,numeric|1:length(5)|2:regex([A-Z]{2,})
```

### YAML Configuration

```yaml
parameters:
  delimiter: ','
  section_separator: '\n\n'
  record_separator: '\n'

sections:
  '0':
    format: 'fl{10,5,15}'
    columns:
      '0':
        - name: 'required'
        - name: 'numeric'
      '1':
        - name: 'length'
          parameters: ['5']
      '2':
        - name: 'regex'
          parameters: ['[A-Z]{2,}']
```

## License

MIT

## Repository

The source code for FlatForge is hosted on GitHub: [https://github.com/akram0zaki/flatforge](https://github.com/akram0zaki/flatforge)

Issues, feature requests, and pull requests can be submitted through the GitHub repository.

## Contributing

Contributions are welcome! Please see the [Contributing Guide](docs/CONTRIBUTING.md) for more information. 