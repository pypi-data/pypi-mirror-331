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

Full documentation is available at: [https://akram0zaki.github.io/flatforge/](https://akram0zaki.github.io/flatforge/)

## Repository and Contributing

The source code for FlatForge is hosted on GitHub: [https://github.com/akram0zaki/flatforge](https://github.com/akram0zaki/flatforge)

Issues, feature requests, and pull requests can be submitted through the GitHub repository.

## License

MIT
