#!/usr/bin/env python
"""
Example script to demonstrate how to use the FlatForge Python API.
"""
import argparse
import os
import sys

# Add the parent directory to the Python path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flatforge import ConfigParserFactory, ValidationProcessor


def main():
    """Main entry point for the example script."""
    parser = argparse.ArgumentParser(description="Validate a flat file using FlatForge")
    
    parser.add_argument("-in", "--input", required=True, help="Input file path")
    parser.add_argument("-format", "--config", required=True, help="Configuration file path")
    parser.add_argument("-out", "--output", help="Output file path")
    parser.add_argument("-exception", "--error", help="Error file path")
    parser.add_argument("-verbose", "--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Parse the configuration file
    config_parser = ConfigParserFactory.get_config_parser(args.config)
    ffmd = config_parser.parse()
    
    # Create a processor and process the input file
    processor = ValidationProcessor(ffmd)
    result = processor.process(args.input, args.output, args.error)
    
    # Print the results
    if args.verbose:
        print(f"Processed {result.processed_records} records")
        print(f"Found {len(result.messages)} messages")
    
    for msg in result.messages:
        print(f"Line {msg.line}, Column {msg.column}: {msg.text} (Severity: {msg.severity.name})")
    
    return 0 if not any(msg.severity.name == "ERROR" for msg in result.messages) else 1


if __name__ == "__main__":
    sys.exit(main()) 