# FlatForge API Reference

This document provides a comprehensive reference for the FlatForge API.

## Table of Contents

- [Configuration](#configuration)
  - [ConfigParser](#configparser)
  - [StringConfigParser](#stringconfigparser)
  - [YamlConfigParser](#yamlconfigparser)
  - [ConfigParserFactory](#configparserfactory)
- [Models](#models)
  - [FileProperties](#fileproperties)
  - [Section](#section)
  - [Column](#column)
  - [Rule](#rule)
  - [ValidationMessage](#validationmessage)
  - [ValidationResult](#validationresult)
- [Processing](#processing)
  - [Processor](#processor)
  - [ValidationProcessor](#validationprocessor)
  - [BaseProcessor](#baseprocessor)
  - [ProcessorFactory](#processorfactory)
- [Validators](#validators)
  - [Validator](#validator)
  - [RequiredValidator](#requiredvalidator)
  - [NumericValidator](#numericvalidator)
  - [LengthValidator](#lengthvalidator)
  - [RegexValidator](#regexvalidator)
  - [InValidator](#invalidator)
  - [RangeValidator](#rangevalidator)
  - [UniqueValidator](#uniquevalidator)
  - [SumValidator](#sumvalidator)
- [Utilities](#utilities)
  - [Utils](#utils)

## Configuration

### ConfigParser

The base class for all configuration parsers.

```python
class ConfigParser:
    def parse(self, config_content):
        """
        Parse the configuration content and return a FileProperties object.
        
        Args:
            config_content (str): The configuration content to parse.
            
        Returns:
            FileProperties: The parsed file properties.
        """
        pass
```

### StringConfigParser

A parser for string-based configurations.

```python
from flatforge.config_parser import StringConfigParser

parser = StringConfigParser()
file_props = parser.parse(config_string)
```

#### Methods

- `parse(config_content)`: Parse the configuration content and return a FileProperties object.

### YamlConfigParser

A parser for YAML-based configurations.

```python
from flatforge.yaml_config_parser import YamlConfigParser

parser = YamlConfigParser()
file_props = parser.parse(yaml_config)
```

#### Methods

- `parse(config_content)`: Parse the configuration content and return a FileProperties object.

### ConfigParserFactory

A factory for creating configuration parsers.

```python
from flatforge.config_parser_factory import ConfigParserFactory

parser = ConfigParserFactory.create_parser("string")
file_props = parser.parse(config_content)
```

#### Methods

- `create_parser(parser_type)`: Create a parser of the specified type.

## Models

### FileProperties

Represents the structure and validation rules for a flat file.

```python
from flatforge.models import FileProperties

file_props = FileProperties()
file_props.parameters = {"delimiter": ",", "section_separator": "\n\n", "record_separator": "\n"}
file_props.sections = {0: section}
```

#### Properties

- `parameters`: A dictionary of file parameters.
- `sections`: A dictionary of sections, keyed by section index.
- `global_rules`: A list of global validation rules.

### Section

Represents a section of a flat file.

```python
from flatforge.models import Section

section = Section()
section.format = "fl{10,5,15}"
section.columns = {0: column}
```

#### Properties

- `format`: The format of the section (e.g., "fl{10,5,15}" for fixed-length with fields of length 10, 5, and 15).
- `columns`: A dictionary of columns, keyed by column index.

### Column

Represents a column in a section.

```python
from flatforge.models import Column

column = Column()
column.rules = [rule]
```

#### Properties

- `rules`: A list of validation rules for the column.

### Rule

Represents a validation rule.

```python
from flatforge.models import Rule

rule = Rule("required")
rule = Rule("length", ["5"])
```

#### Properties

- `name`: The name of the rule.
- `parameters`: A list of parameters for the rule.

### ValidationMessage

Represents a validation message.

```python
from flatforge.models import ValidationMessage

message = ValidationMessage("Value is required", 0)
```

#### Properties

- `text`: The message text.
- `column_index`: The index of the column that failed validation.

### ValidationResult

Represents the result of validating a record.

```python
from flatforge.models import ValidationResult

result = ValidationResult(True, None, 0, 0)
```

#### Properties

- `is_valid`: Whether the record is valid.
- `message`: The validation message, if any.
- `record_index`: The index of the record.
- `section_index`: The index of the section.

## Processing

### Processor

The main processor for validating and processing flat files.

```python
from flatforge.processor import Processor

processor = Processor(file_props)
results = processor.process_file(file_content)
```

#### Methods

- `process_file(file_content)`: Process the file content and return validation results.
- `process_stream(file_stream, chunk_size=1000)`: Process a file stream in chunks.

### ValidationProcessor

A processor that only performs validation.

```python
from flatforge.processor import ValidationProcessor

processor = ValidationProcessor(file_props)
results = processor.process_file(file_content)
```

#### Methods

- `process_file(file_content)`: Process the file content and return validation results.
- `process_stream(file_stream, chunk_size=1000)`: Process a file stream in chunks.

### BaseProcessor

The base class for all processors.

```python
class BaseProcessor:
    def __init__(self, file_properties):
        """
        Initialize the processor with file properties.
        
        Args:
            file_properties (FileProperties): The file properties.
        """
        self.file_properties = file_properties
        
    def process_file(self, file_content):
        """
        Process the file content and return validation results.
        
        Args:
            file_content (str): The file content to process.
            
        Returns:
            dict: A dictionary of validation results, keyed by section index.
        """
        pass
        
    def process_stream(self, file_stream, chunk_size=1000):
        """
        Process a file stream in chunks.
        
        Args:
            file_stream (file): The file stream to process.
            chunk_size (int): The size of each chunk.
            
        Yields:
            dict: A dictionary of validation results for each chunk, keyed by section index.
        """
        pass
```

### ProcessorFactory

A factory for creating processors.

```python
from flatforge.processor_factory import ProcessorFactory

processor = ProcessorFactory.create_processor("validation", file_props)
results = processor.process_file(file_content)
```

#### Methods

- `create_processor(processor_type, file_properties)`: Create a processor of the specified type.

## Validators

### Validator

The base class for all validators.

```python
class Validator:
    def __init__(self, parameters=None):
        """
        Initialize the validator with parameters.
        
        Args:
            parameters (list): The parameters for the validator.
        """
        self.parameters = parameters or []
        
    def validate(self, value, context=None):
        """
        Validate the value.
        
        Args:
            value (str): The value to validate.
            context (dict): The validation context.
            
        Returns:
            tuple: A tuple of (is_valid, message).
        """
        pass
```

### RequiredValidator

Validates that a value is not empty.

```python
from flatforge.validators import RequiredValidator

validator = RequiredValidator()
is_valid, message = validator.validate("")  # False, "Value is required"
```

### NumericValidator

Validates that a value contains only numeric characters.

```python
from flatforge.validators import NumericValidator

validator = NumericValidator()
is_valid, message = validator.validate("123")  # True, None
is_valid, message = validator.validate("abc")  # False, "Value must be numeric"
```

### LengthValidator

Validates that a value has a specific length.

```python
from flatforge.validators import LengthValidator

validator = LengthValidator(["5"])
is_valid, message = validator.validate("12345")  # True, None
is_valid, message = validator.validate("123")  # False, "Value must have length 5"
```

### RegexValidator

Validates that a value matches a regular expression.

```python
from flatforge.validators import RegexValidator

validator = RegexValidator(["[A-Z]{2,}"])
is_valid, message = validator.validate("ABC")  # True, None
is_valid, message = validator.validate("A")  # False, "Value must match pattern [A-Z]{2,}"
```

### InValidator

Validates that a value is in a list of allowed values.

```python
from flatforge.validators import InValidator

validator = InValidator(["A", "B", "C"])
is_valid, message = validator.validate("A")  # True, None
is_valid, message = validator.validate("D")  # False, "Value must be one of: A, B, C"
```

### RangeValidator

Validates that a value is within a numeric range.

```python
from flatforge.validators import RangeValidator

validator = RangeValidator(["1", "10"])
is_valid, message = validator.validate("5")  # True, None
is_valid, message = validator.validate("15")  # False, "Value must be between 1 and 10"
```

### UniqueValidator

Validates that a value is unique across all records.

```python
from flatforge.validators import UniqueValidator

validator = UniqueValidator()
context = {"unique_values": {"0": set()}}
is_valid, message = validator.validate("A", context)  # True, None
context["unique_values"]["0"].add("A")
is_valid, message = validator.validate("A", context)  # False, "Value must be unique"
```

### SumValidator

Validates that the sum of a field equals a specified value.

```python
from flatforge.validators import SumValidator

validator = SumValidator(["1", "100"])
context = {"sum_values": {"1": 0}}
is_valid, message = validator.validate("50", context)  # True, None
context["sum_values"]["1"] += 50
is_valid, message = validator.validate("50", context)  # True, None
# After all records are processed
is_valid, message = validator.validate(None, context)  # True, None
```

## Utilities

### Utils

Utility functions for FlatForge.

```python
from flatforge.utils import parse_fixed_length_format

lengths = parse_fixed_length_format("fl{10,5,15}")  # [10, 5, 15]
```

#### Functions

- `parse_fixed_length_format(format_str)`: Parse a fixed-length format string and return a list of field lengths.
- `split_record(record, delimiter)`: Split a record using the specified delimiter.
- `extract_fields_fixed_length(record, lengths)`: Extract fields from a fixed-length record. 