# FlatForge User Guide

## Introduction

FlatForge is a Python library designed for processing and validating flat files (fixed-length or delimited formats). It provides a flexible and easy-to-use interface for defining file structures, validation rules, and processing logic.

## Installation

You can install FlatForge using pip:

```bash
pip install flatforge
```

For development purposes, you can install additional dependencies:

```bash
pip install flatforge[dev]
```

## Command-Line Interface (CLI)

FlatForge provides a powerful command-line interface that allows you to validate and process flat files directly from your terminal or shell scripts, making it ideal for production environments and automated workflows.

### Basic Usage

The basic syntax for the FlatForge CLI is:

```bash
flatforge [options]
```

### Available Options

```bash
flatforge -in INPUT_FILE -format CONFIG_FILE [options]
```

Required arguments:
- `-in, --input`: Path to the input file to process
- `-format, --config`: Path to the configuration file (YAML or string format)

Optional arguments:
- `-out, --output`: Path to write the output
- `-exception, --error`: Path to write error details
- `-verbose, --verbose`: Enable verbose output
- `-large, --large-file`: Use line-by-line processing for large files (>1GB)
- `-buffer, --buffer-size`: Buffer size in bytes for file processing (default: 8192)
- `-processor, --processor-type`: Type of processor to use (default: validator)
  - Available processors: validator, properties_to_map, record_counter, text_appender, format_converter

### Examples

#### Basic Validation

```bash
flatforge -in data.txt -format config.yaml
```

#### Validation with Error Output

```bash
flatforge -in data.txt -format config.yaml -exception errors.log
```

#### Processing with Output

```bash
flatforge -in data.txt -format config.yaml -out processed.txt -processor text_appender
```

#### Processing Large Files

```bash
flatforge -in large_data.txt -format config.yaml -large -buffer 16384
```

#### Verbose Output

```bash
flatforge -in data.txt -format config.yaml -verbose
```

### Using the CLI in Production Environments

For production environments, you can integrate FlatForge CLI into your shell scripts or automation workflows:

```bash
#!/bin/bash
# Example shell script for processing daily flat files

# Set variables
CONFIG_FILE="/path/to/config.yaml"
INPUT_DIR="/path/to/input"
OUTPUT_DIR="/path/to/output"
LOG_DIR="/path/to/logs"
DATE=$(date +%Y%m%d)

# Process today's file
flatforge \
  -in $INPUT_DIR/data_$DATE.txt \
  -format $CONFIG_FILE \
  -out $OUTPUT_DIR/processed_$DATE.txt \
  -exception $LOG_DIR/errors_$DATE.log \
  > $LOG_DIR/process_$DATE.log 2>&1

# Check exit code
if [ $? -eq 0 ]; then
  echo "Processing completed successfully"
else
  echo "Processing failed, check logs"
  exit 1
fi
```

### Processor Types

FlatForge CLI supports several processor types for different use cases:

1. **validator**: Validates the input file against the configuration rules
2. **properties_to_map**: Extracts key-value pairs from the input file
3. **record_counter**: Counts the number of records in the input file
4. **text_appender**: Appends text to each record in the input file
5. **format_converter**: Converts between different file formats

### Error Handling

When validation errors occur, FlatForge CLI will:

1. Print a summary of the errors to the console
2. Write detailed error information to the error file if specified
3. Return a non-zero exit code

Example error output:
```
Validation completed with 3 errors/warnings
Error details written to 'errors.log'
```

## Configuration Files

FlatForge uses configuration files to define the structure and validation rules for your flat files. You can create configurations in either string-based or YAML-based formats.

### YAML Configuration Format

YAML is the recommended format for configuration files as it's more readable and maintainable:

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

### String Configuration Format

For simpler configurations, you can use the string-based format:

```
[parameters]
delimiter = ,
section_separator = \n\n
record_separator = \n

[section_metadata]
0 = fl{10,5,15}|0:required,numeric|1:length(5)|2:regex([A-Z]{2,})
```

### Configuration Parameters

The `parameters` section defines general settings for the file:

- `delimiter`: The character used to separate fields in delimited files
- `section_separator`: The character(s) used to separate sections in the file
- `record_separator`: The character(s) used to separate records in the file

### Section Definitions

The `sections` (or `section_metadata` in string format) defines the structure and validation rules for each section of the file:

- Section index: The index of the section (starting from 0)
- Format: The format of the section (e.g., `fl{10,5,15}` for fixed-length with fields of length 10, 5, and 15)
- Rules: The validation rules for each field (e.g., `0:required,numeric` for field 0 to be required and numeric)

## Validation Rules

FlatForge supports various validation rules that can be applied to fields in your configuration:

### Basic Rules

- `required`: The field must not be empty
- `numeric`: The field must contain only numeric characters
- `length(n)`: The field must have a length of n
- `regex(pattern)`: The field must match the specified regex pattern
- `in(values)`: The field must be one of the specified values
- `range(min,max)`: The field must be a number within the specified range

### Global Rules

- `unique`: The field must be unique across all records
- `sum(field,value)`: The sum of the specified field must equal the specified value

## Performance Considerations

For large files, FlatForge provides options to optimize processing:

- Use the `-large` flag for files larger than 1GB
- Adjust the buffer size with `-buffer` for optimal performance
- Consider splitting very large files into smaller chunks for parallel processing

## Troubleshooting

### Common Error Messages

- **"Invalid configuration format"**: Check your configuration file syntax
- **"Field validation failed"**: A field in your file doesn't meet the validation rules
- **"File format mismatch"**: The file structure doesn't match the configuration

### Getting Help

If you encounter issues with FlatForge, you can:

1. Check the detailed error messages in your error log
2. Refer to the [API Reference](api_reference.md) for detailed information
3. Check the [GitHub repository](https://github.com/yourusername/flatforge) for known issues

## Conclusion

FlatForge provides a flexible and powerful way to process and validate flat files through its command-line interface. By using the configuration-based approach, you can easily define complex validation rules and processing logic without writing code.

For more advanced usage, including programmatic integration, see the [Developer Guide](developer_guide.md). 