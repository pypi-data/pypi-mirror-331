"""
Command-line interface for FlatForge.
"""
import argparse
import os
import sys
from typing import List, Optional

from .config_parser_factory import ConfigParserFactory
# from .processor import ValidationProcessor
from .processor_factory import ProcessorFactory


def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(description="FlatForge - Validate and process flat files")
    
    parser.add_argument("-in", "--input", required=True, help="Input file path")
    parser.add_argument("-out", "--output", help="Output file path")
    parser.add_argument("-exception", "--error", help="Error file path")
    parser.add_argument("-format", "--config", required=True, help="Configuration file path")
    parser.add_argument("-verbose", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-large", "--large-file", action="store_true", 
                        help="Use line-by-line processing for large files (>1GB)")
    parser.add_argument("-buffer", "--buffer-size", type=int, default=8192,
                        help="Buffer size in bytes for file processing (default: 8192)")
    parser.add_argument("-processor", "--processor-type", default="validator",
                        choices=["validator", "properties_to_map", "record_counter", "text_appender", "format_converter"],
                        help="Type of processor to use (default: validator)")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.isfile(args.input):
        print(f"Error: Input file '{args.input}' does not exist")
        sys.exit(1)
    
    # Check if config file exists
    if not os.path.isfile(args.config):
        print(f"Error: Configuration file '{args.config}' does not exist")
        sys.exit(1)
    
    # Read config file
    try:
        with open(args.config, 'r') as f:
            config_text = f.read()
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        sys.exit(1)
    
    # Parse config using the appropriate parser
    try:
        config_parser = ConfigParserFactory.get_config_parser(args.config)
        ffmd = config_parser.parse(config_text)
    except Exception as e:
        print(f"Error parsing configuration: {e}")
        sys.exit(1)
    
    # Open output and error streams if specified
    out_stream = None
    error_stream = None
    
    try:
        if args.output:
            out_stream = open(args.output, 'w', encoding=ffmd.encoding)
        
        if args.error:
            error_stream = open(args.error, 'w', encoding=ffmd.encoding)
        
        # Create processor based on processor type
        processor = ProcessorFactory.get_processor(
            args.processor_type, 
            ffmd, 
            out_stream, 
            error_stream, 
            args.buffer_size
        )
        
        if not processor:
            print(f"Error: Unknown processor type: {args.processor_type}")
            sys.exit(1)
        
        # Process file
        try:
            if args.verbose:
                print(f"Processing file '{args.input}' with processor '{args.processor_type}'")
            
            # For validator processor, handle large files differently
            if args.processor_type == "validator":
                if args.large_file:
                    if args.verbose:
                        print(f"Using line-by-line processing for large file")
                    messages = processor.process_line_by_line(args.input, args.output, args.error)
                else:
                    messages = processor.process(args.input, args.output, args.error)
                
                # Print validation results
                if args.verbose:
                    print(f"Processed file '{args.input}'")
                    print(f"Found {len(messages)} validation messages")
                    
                    for message in messages:
                        print(f"{message.code}: {message.severity} in section {message.section_number}, column {message.column_number} - {message.value}")
                
                if messages:
                    print(f"Validation completed with {len(messages)} errors/warnings")
                    if args.error:
                        print(f"Error details written to '{args.error}'")
                else:
                    print("Validation completed successfully with no errors")
            else:
                # For other processors, use a simpler processing approach
                process_with_processor(processor, args.input, ffmd, args.verbose)
                
                # Print processor-specific results
                if args.processor_type == "record_counter":
                    print(f"Total records: {processor.get_record_count()}")
                elif args.processor_type == "properties_to_map":
                    print(f"Processed {len(processor.get_payload())} key/value pairs")
                elif args.processor_type == "text_appender":
                    print(f"Appended {len(processor.get_file_contents().splitlines())} lines")
                
                if args.output:
                    print(f"Output written to '{args.output}'")
        
        except Exception as e:
            print(f"Error processing file: {e}")
            sys.exit(1)
    
    finally:
        # Close streams
        if out_stream:
            out_stream.close()
        
        if error_stream:
            error_stream.close()


def process_with_processor(processor, input_file, ffmd, verbose=False):
    """Process a file with a non-validator processor."""
    # Initialize processor
    processor.initialize(ffmd, -1)  # We don't know total records yet
    
    # Process file line by line
    record_number = 0
    section_number = "0"
    record_number_within_section = 0
    
    with open(input_file, 'r', encoding=ffmd.encoding) as f:
        for line in f:
            # Check for section separator
            if ffmd.section_separator and ffmd.section_separator in line:
                # Move to next section
                section_number = str(int(section_number) + 1)
                record_number_within_section = 0
                
                # Process the rest of the line after the section separator
                remaining = line.split(ffmd.section_separator, 1)[1]
                if remaining:
                    processor.process_record(
                        remaining, 
                        section_number, 
                        record_number, 
                        record_number_within_section, 
                        ffmd, 
                        False
                    )
                    record_number += 1
                    record_number_within_section += 1
            else:
                # Process the record
                processor.process_record(
                    line, 
                    section_number, 
                    record_number, 
                    record_number_within_section, 
                    ffmd, 
                    False
                )
                record_number += 1
                record_number_within_section += 1
    
    # Finalize processing
    processor.finalize(section_number, record_number, ffmd, False)
    
    if verbose:
        print(f"Processed {record_number} records in {int(section_number) + 1} sections")


if __name__ == "__main__":
    main() 