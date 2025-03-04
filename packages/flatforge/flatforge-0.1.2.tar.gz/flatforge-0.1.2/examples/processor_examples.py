#!/usr/bin/env python
"""
Examples of using different processors in FlatForge.

This script demonstrates how to use the various processors available in FlatForge:
- ValidationProcessor
- PropertiesToMapCopier
- RecordCounter
- TextAppender
- BaseFormatConverter

Usage:
    python processor_examples.py
"""
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import flatforge
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flatforge.config_parser_factory import ConfigParserFactory
from flatforge.processor_factory import ProcessorFactory
from flatforge.models import FlatFileMetaData
from flatforge.utils import TextFormat


def create_sample_config():
    """Create a sample configuration for testing."""
    ffmd = FlatFileMetaData()
    ffmd.text_format_code = TextFormat.DELIMITED.value
    ffmd.field_separator = ","
    ffmd.record_separator = "\n"
    ffmd.encoding = "utf-8"
    
    return ffmd


def create_sample_files():
    """Create sample files for testing."""
    # Create a sample delimited file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("John,Doe,30,New York\n")
        f.write("Jane,Smith,25,Los Angeles\n")
        f.write("Bob,Johnson,40,Chicago\n")
        delimited_file = f.name
    
    # Create a sample properties file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("name=John Doe\n")
        f.write("age=30\n")
        f.write("# This is a comment\n")
        f.write("city=New York\n")
        f.write("country=USA\n")
        properties_file = f.name
    
    return delimited_file, properties_file


def example_validator(config, input_file):
    """Example of using the ValidationProcessor."""
    print("\n=== ValidationProcessor Example ===")
    
    # Create processor
    processor = ProcessorFactory.get_processor("validator", config)
    
    # Process file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as out_f:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as err_f:
            messages = processor.process(input_file, out_f.name, err_f.name)
    
    # Print results
    print(f"Processed file: {input_file}")
    print(f"Found {len(messages)} validation messages")
    
    # Clean up
    os.unlink(out_f.name)
    os.unlink(err_f.name)


def example_properties_to_map(config, input_file):
    """Example of using the PropertiesToMapCopier."""
    print("\n=== PropertiesToMapCopier Example ===")
    
    # Update config for properties file
    config.field_separator = "="
    
    # Create processor
    processor = ProcessorFactory.get_processor("properties_to_map", config)
    processor.initialize(config, -1)
    
    # Process file manually
    record_number = 0
    with open(input_file, 'r', encoding=config.encoding) as f:
        for line in f:
            processor.process_record(line, "0", record_number, record_number, config, False)
            record_number += 1
    
    # Terminate processing
    processor.terminate(1, record_number, config, False)
    
    # Print results
    properties = processor.get_payload()
    print(f"Processed file: {input_file}")
    print(f"Found {len(properties)} properties:")
    for key, value in properties.items():
        print(f"  {key} = {value}")


def example_record_counter(config, input_file):
    """Example of using the RecordCounter."""
    print("\n=== RecordCounter Example ===")
    
    # Create processor
    processor = ProcessorFactory.get_processor("record_counter", config)
    processor.initialize(config, -1)
    
    # Process file manually
    record_number = 0
    with open(input_file, 'r', encoding=config.encoding) as f:
        for line in f:
            processor.process_record(line, "0", record_number, record_number, config, False)
            record_number += 1
    
    # Terminate processing
    processor.terminate(1, record_number, config, False)
    
    # Print results
    print(f"Processed file: {input_file}")
    print(f"Total records: {processor.get_record_count()}")


def example_text_appender(config, input_file):
    """Example of using the TextAppender."""
    print("\n=== TextAppender Example ===")
    
    # Create processor
    processor = ProcessorFactory.get_processor("text_appender", config)
    processor.initialize(config, -1)
    
    # Process file manually
    record_number = 0
    with open(input_file, 'r', encoding=config.encoding) as f:
        for line in f:
            processor.process_record(line, "0", record_number, record_number, config, False)
            record_number += 1
    
    # Terminate processing
    processor.terminate(1, record_number, config, False)
    
    # Print results
    print(f"Processed file: {input_file}")
    print(f"File contents:")
    print(processor.get_file_contents())


def example_format_converter(config, input_file):
    """Example of using the BaseFormatConverter."""
    print("\n=== BaseFormatConverter Example ===")
    
    # Create output file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as out_f:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as err_f:
            # Create processor with output streams
            processor = ProcessorFactory.get_processor(
                "format_converter", config, out_f, err_f
            )
            processor.initialize(config, -1)
            
            # Process file manually
            record_number = 0
            with open(input_file, 'r', encoding=config.encoding) as f:
                for line in f:
                    processor.process_record(line, "0", record_number, record_number, config, False)
                    record_number += 1
            
            # Terminate processing
            processor.terminate(1, record_number, config, False)
    
    # Print results
    print(f"Processed file: {input_file}")
    print(f"Output written to: {out_f.name}")
    
    # Read and print output
    with open(out_f.name, 'r', encoding=config.encoding) as f:
        output = f.read()
    
    print("Output contents:")
    print(output)
    
    # Clean up
    os.unlink(out_f.name)
    os.unlink(err_f.name)


def main():
    """Run all processor examples."""
    print("FlatForge Processor Examples")
    print("===========================")
    
    # Create sample configuration and files
    config = create_sample_config()
    input_file, output_dir = create_sample_files()
    
    # Run examples
    print("\n1. Validation Processor Example:")
    example_validator(config, input_file)
    
    print("\n2. Properties To Map Copier Example:")
    example_properties_to_map(config, input_file)
    
    print("\n3. Record Counter Example:")
    example_record_counter(config, input_file)
    
    print("\n4. Text Appender Example:")
    example_text_appender(config, input_file)
    
    print("\n5. Format Converter Example:")
    example_format_converter(config, input_file)
    
    print("\nAll examples completed. Temporary files created in:", output_dir)
    print("Remember to delete these files when you're done.")


if __name__ == "__main__":
    main() 