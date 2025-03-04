# FlatForge Architecture

This document provides an overview of the FlatForge architecture, including design patterns, component interactions, and extensibility points.

## Overview

FlatForge is designed with a focus on flexibility, extensibility, and separation of concerns. The architecture follows several design patterns to achieve these goals:

1. **Factory Pattern**: Used for creating parsers and processors.
2. **Strategy Pattern**: Used for implementing different validation strategies.
3. **Composite Pattern**: Used for combining multiple validators.
4. **Builder Pattern**: Used for constructing complex file property objects.

## Component Diagram

```
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
| ConfigParser   |---->| FileProperties |<----| Processor      |
|                |     |                |     |                |
+----------------+     +----------------+     +----------------+
        |                      |                      |
        v                      v                      v
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
| StringConfig   |     | Section        |     | Validation     |
| Parser         |     |                |     | Processor      |
|                |     +----------------+     |                |
+----------------+             |              +----------------+
        |                      v                      |
        v                +----------------+           v
+----------------+       |                |    +----------------+
|                |       | Column         |    |                |
| YamlConfig     |       |                |    | Custom         |
| Parser         |       +----------------+    | Processor      |
|                |               |             |                |
+----------------+               v             +----------------+
                         +----------------+
                         |                |
                         | Rule           |
                         |                |
                         +----------------+
                                 |
                                 v
                         +----------------+
                         |                |
                         | Validator      |
                         |                |
                         +----------------+
                                 |
                                 v
                         +----------------+
                         |                |
                         | RequiredValidator,
                         | NumericValidator,
                         | etc.           |
                         +----------------+
```

## Core Components

### Configuration Parsing

The configuration parsing components are responsible for parsing different configuration formats and creating a `FileProperties` object.

#### ConfigParser

The base class for all configuration parsers. It defines the interface for parsing configurations.

#### StringConfigParser

Parses string-based configurations in a simple format:

```
[parameters]
delimiter = ,
section_separator = \n\n
record_separator = \n

[section_metadata]
0 = fl{10,5,15}|0:required,numeric|1:length(5)|2:regex([A-Z]{2,})
```

#### YamlConfigParser

Parses YAML-based configurations:

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

#### ConfigParserFactory

A factory for creating configuration parsers based on the configuration format.

### Models

The model components represent the structure and validation rules for a flat file.

#### FileProperties

The top-level model that represents the structure and validation rules for a flat file. It contains:

- Parameters: General settings like delimiters and separators.
- Sections: Different parts of the file, each with its own format and rules.
- Global Rules: Rules that apply across multiple records.

#### Section

Represents a section of a flat file. It contains:

- Format: The format of the section (e.g., fixed-length or delimited).
- Columns: The columns in the section, each with its own validation rules.

#### Column

Represents a column in a section. It contains:

- Rules: The validation rules for the column.

#### Rule

Represents a validation rule. It contains:

- Name: The name of the rule.
- Parameters: The parameters for the rule.

#### ValidationMessage

Represents a validation message. It contains:

- Text: The message text.
- Column Index: The index of the column that failed validation.

#### ValidationResult

Represents the result of validating a record. It contains:

- Is Valid: Whether the record is valid.
- Message: The validation message, if any.
- Record Index: The index of the record.
- Section Index: The index of the section.

### Processing

The processing components are responsible for validating and processing flat files.

#### Processor

The main processor for validating and processing flat files. It uses the `FileProperties` object to validate file content.

#### ValidationProcessor

A processor that only performs validation, without any additional processing.

#### BaseProcessor

The base class for all processors. It defines the interface for processing files.

#### ProcessorFactory

A factory for creating processors based on the processing type.

### Validators

The validator components are responsible for validating individual fields.

#### Validator

The base class for all validators. It defines the interface for validating values.

#### RequiredValidator, NumericValidator, etc.

Concrete validator implementations for different validation rules.

## Extensibility Points

FlatForge is designed to be extensible at several points:

### Custom Validators

You can create custom validators by extending the `Validator` class:

```python
from flatforge.validators import Validator

class MyValidator(Validator):
    def __init__(self, parameters=None):
        super().__init__(parameters)
        
    def validate(self, value, context=None):
        # Implement your validation logic here
        if not my_validation_condition:
            return False, "Validation failed"
        return True, None
```

### Custom Processors

You can create custom processors by extending the `BaseProcessor` class:

```python
from flatforge.processors import BaseProcessor

class MyProcessor(BaseProcessor):
    def __init__(self, file_properties):
        super().__init__(file_properties)
        
    def process_file(self, file_content):
        # Implement your processing logic here
        return results
```

### Custom Configuration Parsers

You can create custom configuration parsers by extending the `ConfigParser` class:

```python
from flatforge.config_parser import ConfigParser

class MyConfigParser(ConfigParser):
    def parse(self, config_content):
        # Implement your parsing logic here
        return file_properties
```

## Performance Considerations

FlatForge is designed to handle large files efficiently. It provides a streaming API for processing files in chunks:

```python
with open('large_file.txt', 'r') as f:
    for chunk in processor.process_stream(f):
        # Process each chunk of results
        pass
```

The streaming API reduces memory usage by processing the file in chunks, rather than loading the entire file into memory.

## Error Handling

FlatForge provides detailed error reporting through the `ValidationResult` class. Each validation error includes:

- The section index
- The record index
- The column index
- A descriptive error message

This detailed error reporting helps users quickly identify and fix validation issues.

## Future Directions

Future enhancements to the FlatForge architecture may include:

1. **Parallel Processing**: Adding support for parallel processing of large files.
2. **Custom Output Formats**: Adding support for custom output formats (e.g., JSON, CSV).
3. **Integration with Data Processing Frameworks**: Adding support for integration with data processing frameworks like Apache Spark or Apache Beam.
4. **Web Interface**: Adding a web interface for configuring and running validations.
5. **Real-time Validation**: Adding support for real-time validation of streaming data. 