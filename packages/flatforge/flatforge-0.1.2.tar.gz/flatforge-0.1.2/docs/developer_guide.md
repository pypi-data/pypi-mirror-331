# FlatForge Developer Guide

## Introduction

This guide is intended for developers who want to use FlatForge programmatically or extend its functionality. It covers the core APIs, extension points, and architectural considerations.

## Programmatic Usage

### Creating a Configuration

FlatForge uses a configuration to define the structure and validation rules for flat files. You can create a configuration using either string-based or YAML-based formats.

#### String-Based Configuration

```python
from flatforge.config_parser import StringConfigParser

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
```

#### YAML-Based Configuration

```python
from flatforge.yaml_config_parser import YamlConfigParser

# Create a configuration
config = """
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
"""

# Parse the configuration
parser = YamlConfigParser()
file_props = parser.parse(config)
```

### Processing a File

Once you have a configuration, you can use it to process a file:

```python
from flatforge.processor import Processor

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

### Using the Factory Pattern

FlatForge provides factory classes for creating parsers and processors:

```python
from flatforge.config_parser_factory import ConfigParserFactory
from flatforge.processor_factory import ProcessorFactory

# Create a parser
parser = ConfigParserFactory.create_parser("yaml")
file_props = parser.parse(config_content)

# Create a processor
processor = ProcessorFactory.create_processor("validation", file_props)
results = processor.process_file(file_content)
```

### Processing Large Files

For large files, use the streaming API to process the file in chunks:

```python
with open('large_file.txt', 'r') as f:
    for chunk in processor.process_stream(f, chunk_size=8192):
        # Process each chunk of results
        for section_index, section_results in chunk.items():
            for result in section_results:
                if not result.is_valid:
                    print(f"Error in section {section_index}, record {result.record_index}: {result.message.text}")
```

## Extending FlatForge

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

To register your custom validator:

```python
from flatforge.validator_factory import ValidatorFactory

ValidatorFactory.register_validator("my_validator", MyValidator)
```

Then you can use it in your configuration:

```yaml
sections:
  '0':
    columns:
      '0':
        - name: 'my_validator'
          parameters: ['param1', 'param2']
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
        
    def process_stream(self, file_stream, chunk_size=1000):
        # Implement your streaming logic here
        for chunk in self._read_chunks(file_stream, chunk_size):
            yield self.process_file(chunk)
```

To register your custom processor:

```python
from flatforge.processor_factory import ProcessorFactory

ProcessorFactory.register_processor("my_processor", MyProcessor)
```

Then you can use it:

```python
processor = ProcessorFactory.create_processor("my_processor", file_props)
results = processor.process_file(file_content)
```

### Custom Configuration Parsers

You can create custom configuration parsers by extending the `ConfigParser` class:

```python
from flatforge.config_parser import ConfigParser

class MyConfigParser(ConfigParser):
    def parse(self, config_content):
        # Implement your parsing logic here
        file_properties = FileProperties()
        # Populate file_properties
        return file_properties
```

To register your custom parser:

```python
from flatforge.config_parser_factory import ConfigParserFactory

ConfigParserFactory.register_parser("my_format", MyConfigParser)
```

Then you can use it:

```python
parser = ConfigParserFactory.create_parser("my_format")
file_props = parser.parse(config_content)
```

## Core API Reference

### Models

#### FileProperties

The top-level model that represents the structure and validation rules for a flat file.

```python
from flatforge.models import FileProperties

file_props = FileProperties()
file_props.parameters = {"delimiter": ",", "section_separator": "\n\n", "record_separator": "\n"}
file_props.sections = {0: section}
file_props.global_rules = [rule]
```

#### Section

Represents a section of a flat file.

```python
from flatforge.models import Section

section = Section()
section.format = "fl{10,5,15}"
section.columns = {0: column}
```

#### Column

Represents a column in a section.

```python
from flatforge.models import Column

column = Column()
column.rules = [rule]
```

#### Rule

Represents a validation rule.

```python
from flatforge.models import Rule

rule = Rule("required")
rule = Rule("length", ["5"])
```

#### ValidationMessage

Represents a validation message.

```python
from flatforge.models import ValidationMessage

message = ValidationMessage("Value is required", 0)
```

#### ValidationResult

Represents the result of validating a record.

```python
from flatforge.models import ValidationResult

result = ValidationResult(True, None, 0, 0)
```

### Validators

FlatForge includes several built-in validators:

- `RequiredValidator`: Validates that a value is not empty
- `NumericValidator`: Validates that a value contains only numeric characters
- `LengthValidator`: Validates that a value has a specific length
- `RegexValidator`: Validates that a value matches a regular expression
- `InValidator`: Validates that a value is in a list of allowed values
- `RangeValidator`: Validates that a value is within a numeric range
- `UniqueValidator`: Validates that a value is unique across all records
- `SumValidator`: Validates that the sum of a field equals a specified value

Example usage:

```python
from flatforge.validators import RequiredValidator, NumericValidator

required_validator = RequiredValidator()
is_valid, message = required_validator.validate("")  # False, "Value is required"

numeric_validator = NumericValidator()
is_valid, message = numeric_validator.validate("123")  # True, None
```

## Architecture Overview

FlatForge is designed with a focus on flexibility, extensibility, and separation of concerns. The architecture follows several design patterns:

1. **Factory Pattern**: Used for creating parsers and processors
2. **Strategy Pattern**: Used for implementing different validation strategies
3. **Composite Pattern**: Used for combining multiple validators
4. **Builder Pattern**: Used for constructing complex file property objects

### Component Diagram

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

## Performance Considerations

FlatForge is designed to handle large files efficiently. Here are some tips for optimizing performance:

1. **Use the Streaming API**: For large files, use the `process_stream` method to process the file in chunks.
2. **Optimize Chunk Size**: Adjust the chunk size based on your memory constraints and file size.
3. **Minimize Validation Rules**: Only use the validation rules you need, as each rule adds processing overhead.
4. **Use Fixed-Length Format**: For very large files, fixed-length format can be faster to process than delimited format.
5. **Consider Parallel Processing**: For very large files, consider implementing parallel processing using Python's multiprocessing module.

## Error Handling

FlatForge provides detailed error reporting through the `ValidationResult` class. Each validation error includes:

- The section index
- The record index
- The column index
- A descriptive error message

Example error handling:

```python
for section_index, section_results in results.items():
    for result in section_results:
        if not result.is_valid:
            print(f"Error in section {section_index}, record {result.record_index}, column {result.message.column_index}: {result.message.text}")
```

## Testing Your Extensions

When creating custom validators or processors, it's important to test them thoroughly. FlatForge includes a testing framework to help with this:

```python
from flatforge.testing import ValidatorTestCase

class MyValidatorTest(ValidatorTestCase):
    def test_my_validator(self):
        validator = MyValidator(["param1", "param2"])
        self.assert_valid(validator, "valid_value")
        self.assert_invalid(validator, "invalid_value", "Expected error message")
```

## Conclusion

This developer guide provides an overview of how to use FlatForge programmatically and how to extend its functionality. For more detailed information, see the [API Reference](api_reference.md) and [Architecture](design/architecture.md) documentation.

If you have any questions or need further assistance, please check the [GitHub repository](https://github.com/yourusername/flatforge) or contact the maintainers. 