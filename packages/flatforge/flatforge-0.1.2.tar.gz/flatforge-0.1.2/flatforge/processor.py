"""
Core processing module for FlatForge.
"""
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set, Protocol, Type, Union, TextIO
from collections import defaultdict

from .models import Rule, GlobalRule, Section, FileProperties, RuleResult, Message, CellId, MessageSeverity
from .validators import (
    Validator, ValidationContext, NumberValidator, StringValidator, ChoiceValidator, DateValidator, 
    SumCrValidator, CountCrValidator, PrefixValidator, SuffixValidator, 
    PutValidator, TrimValidator, UniqueValidator, IChoiceValidator
)
from .utils import TextFormat, FlatFileError, ValidationError, ConfigurationError, StringUtils


# Set up logging
logger = logging.getLogger(__name__)


class ValidatorFactory:
    """Factory for creating validators."""
    
    _validators = {
        "num": NumberValidator(),
        "str": StringValidator(),
        "choice": ChoiceValidator(),
        "ichoice": IChoiceValidator(),
        "date": DateValidator(),
        "prefix": PrefixValidator(),
        "suffix": SuffixValidator(),
        "put": PutValidator(),
        "trim": TrimValidator(),
        "unique": UniqueValidator(),
        "cr_sum": SumCrValidator(),
        "cr_count": CountCrValidator()
    }
    
    @classmethod
    def get_validator(cls, check_name: str) -> Optional[Validator]:
        """Get a validator for a check name."""
        return cls._validators.get(check_name)
    
    @classmethod
    def register_validator(cls, check_name: str, validator: Validator) -> None:
        """Register a validator for a check name."""
        cls._validators[check_name] = validator


class Processor:
    """
    Main processor class for validating flat files against configuration.
    """
    
    def __init__(self, file_props: FileProperties):
        """
        Initialize the processor with file properties.
        
        Args:
            file_props: The file properties containing validation rules
        """
        self.file_props = file_props
        self.results = {}
        self.global_results = {}
    
    def process_file(self, file_content: str) -> Dict[str, List[RuleResult]]:
        """Process a file using the configured file properties."""
        # Reset results
        self.results = {}
        self.global_results = {}
        
        # Split file into sections
        sections = self._split_file_into_sections(file_content)
        
        # Process each section
        for section_index, section_content in sections.items():
            section = self.file_props.get_section(section_index)
            if section:
                self._process_section(section, section_content)
        
        # Process global rules
        self._process_global_rules()
        
        # Combine results
        all_results = self.results.copy()
        all_results.update(self.global_results)
        
        return all_results
    
    def _split_file_into_sections(self, file_content: str) -> Dict[str, List[str]]:
        """Split a file into sections based on the file properties."""
        sections = {}
        
        # Get section separator from file properties
        section_separator = self.file_props.get_parameter("section_separator", "\n\n")
        
        # Split file content into sections
        raw_sections = file_content.split(section_separator)
        
        # Assign sections to their indices
        for section_index, section in self.file_props.sections.items():
            section_idx = int(section_index)
            if section_idx < len(raw_sections):
                # Get record separator from file properties
                record_separator = self.file_props.get_parameter("record_separator", "\n")
                
                # Split section content into records
                records = raw_sections[section_idx].strip().split(record_separator)
                sections[section_index] = records
        
        return sections
    
    def _process_section(self, section: Section, records: List[str]) -> None:
        """Process a section of the file."""
        section_index = section.index
        
        # Initialize results for this section
        if section_index not in self.results:
            self.results[section_index] = []
        
        # Process each record in the section
        for record_index, record in enumerate(records):
            # Process each column in the record
            self._process_record(section, record, record_index)
    
    def _process_record(self, section: Section, record: str, record_index: int) -> None:
        """Process a record using the rules defined for each column."""
        section_index = section.index
        
        # Split record into columns based on section format
        columns = self._split_record_into_columns(section, record)
        
        # Process each column in the record
        for column_index, rules in section.rules.items():
            if column_index < len(columns):
                column_value = columns[column_index]
                
                # Process each rule for this column
                for rule in rules:
                    # Skip global rules - they are processed separately
                    if isinstance(rule, GlobalRule):
                        continue
                    
                    # Process the rule
                    result = self._process_rule(rule, column_value, section_index, column_index, record_index)
                    
                    # Add result to the results list
                    if result:
                        self.results[section_index].append(result)
    
    def _split_record_into_columns(self, section: Section, record: str) -> List[str]:
        """Split a record into columns based on the section format."""
        columns = []
        
        # Get section format
        section_format = section.section_format
        
        if section_format:
            if section_format.startswith("fl{"):
                # Fixed length format
                format_parts = section_format.split("{")
                if len(format_parts) > 1:
                    lengths_str = format_parts[1].rstrip("}")
                    lengths = [int(l) for l in lengths_str.split(",")]
                    
                    # Split record into columns based on lengths
                    start = 0
                    for length in lengths:
                        if start < len(record):
                            end = min(start + length, len(record))
                            columns.append(record[start:end])
                            start = end
                        else:
                            columns.append("")
            elif section_format.startswith("del"):
                # Delimited format
                delimiter = self.file_props.get_parameter("delimiter", ",")
                columns = record.split(delimiter)
        else:
            # Default to treating the entire record as a single column
            columns = [record]
        
        return columns
    
    def _process_rule(self, rule: Rule, value: str, section_index: str, column_index: int, record_index: int) -> Optional[RuleResult]:
        """Process a rule on a value."""
        # Get rule handler
        handler = self._get_rule_handler(rule.name)
        
        if handler:
            # Call the rule handler
            is_valid, message = handler(value, rule.parameters)
            
            if not is_valid and not rule.is_optional:
                # Create a result for the failed rule
                return RuleResult(
                    rule=rule,
                    value=value,
                    is_valid=False,
                    message=Message(
                        text=message,
                        section_index=section_index,
                        column_index=column_index,
                        record_index=record_index
                    )
                )
        
        return None
    
    def _process_global_rules(self) -> None:
        """Process all global rules."""
        for rule in self.file_props.global_rules:
            # Initialize results for this section if not already done
            section_index = rule.section_index
            if section_index not in self.global_results:
                self.global_results[section_index] = []
            
            # Get the section and column to watch
            watch_section = self.file_props.get_section(rule.section_index)
            if not watch_section:
                continue
            
            # Process the global rule
            result = self._process_global_rule(rule)
            
            # Add result to the results list
            if result:
                self.global_results[section_index].append(result)
    
    def _process_global_rule(self, rule: GlobalRule) -> Optional[RuleResult]:
        """Process a global rule."""
        # Get rule handler
        handler = self._get_rule_handler(rule.name)
        
        if handler:
            # Get the values to process
            values = self._get_values_for_global_rule(rule)
            
            # Call the rule handler
            is_valid, message = handler(values, rule.parameters)
            
            if not is_valid and not rule.is_optional:
                # Create a result for the failed rule
                return RuleResult(
                    rule=rule,
                    value=str(values),
                    is_valid=False,
                    message=Message(
                        text=message,
                        section_index=rule.section_index,
                        column_index=rule.column_index
                    )
                )
        
        return None
    
    def _get_values_for_global_rule(self, rule: GlobalRule) -> List[str]:
        """Get the values to process for a global rule."""
        values = []
        
        # Get the section to watch
        watch_section = self.file_props.get_section(rule.section_index)
        if not watch_section:
            return values
        
        # Get the column to watch
        column_index = rule.column_index
        
        # Get all records for this section
        section_records = self._get_section_records(rule.section_index)
        
        # Extract values from the specified column
        for record in section_records:
            columns = self._split_record_into_columns(watch_section, record)
            if column_index < len(columns):
                values.append(columns[column_index])
        
        return values
    
    def _get_section_records(self, section_index: str) -> List[str]:
        """Get all records for a section."""
        # This would typically come from the processed file data
        # For now, we'll return an empty list as a placeholder
        return []
    
    def _get_rule_handler(self, rule_name: str):
        """Get the handler function for a rule."""
        # This would typically be a mapping of rule names to handler functions
        # For now, we'll return a simple handler that always returns True
        return lambda value, params: (True, "")


class ValidationProcessor:
    """Processor for validating flat files."""
    
    def __init__(self, ffmd: FileProperties, validator_factory: ValidatorFactory = None, buffer_size: int = 8192):
        """Initialize the processor."""
        self.ffmd = ffmd
        self.validator_factory = validator_factory or ValidatorFactory
        self.error_handler = None
        self.crc_validators = {}
        self.buffer_size = buffer_size  # Size of buffer in bytes
        self.errors = []
        self.warnings = []
        self.out_stream = None
        self.error_stream = None
        
        # Initialize cross-record validators
        for global_rule in ffmd.global_rules:
            validator_name = global_rule.name
            validator = self.validator_factory.get_validator(validator_name)
            if validator:
                self.crc_validators[global_rule.name] = validator
    
    def set_out_stream(self, out_stream: Optional[TextIO]) -> None:
        """Set the output stream.
        
        Args:
            out_stream: The output stream
        """
        self.out_stream = out_stream
    
    def set_error_stream(self, error_stream: Optional[TextIO]) -> None:
        """Set the error stream.
        
        Args:
            error_stream: The error stream
        """
        self.error_stream = error_stream
    
    def process(self, input_file: str, output_file: Optional[str] = None, error_file: Optional[str] = None) -> List[Message]:
        """Process a file and return any validation messages."""
        all_messages = []
        
        # Use streams if they were set directly
        output_file = output_file or (self.out_stream.name if self.out_stream else None)
        error_file = error_file or (self.error_stream.name if self.error_stream else None)
        
        # Convert to Path objects
        input_path = Path(input_file)
        output_path = Path(output_file) if output_file else None
        error_path = Path(error_file) if error_file else None
        
        # Check if input file exists
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Process the file in a buffered manner
        if self.ffmd.section_separator:
            # For files with sections, we need to process section by section
            all_messages = self._process_file_with_sections(input_path, output_path)
        else:
            # For files without sections, we can process record by record
            all_messages = self._process_file_without_sections(input_path, output_path)
        
        # Write error file if specified
        if error_path and all_messages:
            self._write_error_file(error_path, all_messages)
        
        return all_messages
    
    def _process_file_without_sections(self, input_path: Path, output_path: Optional[Path] = None) -> List[Message]:
        """Process a file without sections in a buffered manner."""
        all_messages = []
        record_buffer = []
        record_number = 0
        
        # Open output file if specified
        output_file = None
        if output_path:
            output_file = output_path.open('w', encoding=self.ffmd.encoding)
        
        try:
            # Process the file line by line
            with input_path.open('r', encoding=self.ffmd.encoding) as f:
                current_record = ""
                
                for line in f:
                    # Check if this line completes a record
                    if self.ffmd.record_separator in line:
                        parts = line.split(self.ffmd.record_separator)
                        
                        for i, part in enumerate(parts):
                            if i < len(parts) - 1:  # Not the last part
                                current_record += part
                                
                                # Process the complete record
                                if not self.ffmd.ignore_blank_rows or current_record.strip():
                                    messages = self._process_record("0", record_number, current_record)
                                    all_messages.extend(messages)
                                    record_number += 1
                                
                                # Write to output if specified
                                if output_file:
                                    output_file.write(current_record)
                                    output_file.write(self.ffmd.record_separator)
                                
                                current_record = ""
                            else:  # Last part
                                current_record = part
                    else:
                        current_record += line
                
                # Process any remaining content
                if current_record:
                    if not self.ffmd.ignore_blank_rows or current_record.strip():
                        messages = self._process_record("0", record_number, current_record)
                        all_messages.extend(messages)
                    
                    # Write to output if specified
                    if output_file:
                        output_file.write(current_record)
        finally:
            # Close output file if opened
            if output_file:
                output_file.close()
        
        return all_messages
    
    def _process_file_with_sections(self, input_path: Path, output_path: Optional[Path] = None) -> List[Message]:
        """Process a file with sections in a buffered manner."""
        all_messages = []
        section_buffer = []
        current_section = ""
        section_number = 0
        
        # Open output file if specified
        output_file = None
        if output_path:
            output_file = output_path.open('w', encoding=self.ffmd.encoding)
        
        try:
            # Process the file in chunks
            with input_path.open('r', encoding=self.ffmd.encoding) as f:
                for line in f:
                    # Check if this line contains a section separator
                    if self.ffmd.section_separator in line:
                        parts = line.split(self.ffmd.section_separator)
                        
                        for i, part in enumerate(parts):
                            if i < len(parts) - 1:  # Not the last part
                                current_section += part
                                
                                # Process the complete section
                                messages = self._process_section(str(section_number), current_section)
                                all_messages.extend(messages)
                                section_number += 1
                                
                                # Write to output if specified
                                if output_file:
                                    if section_number > 1:  # Not the first section
                                        output_file.write(self.ffmd.section_separator)
                                    output_file.write(current_section)
                                
                                current_section = ""
                            else:  # Last part
                                current_section = part
                    else:
                        current_section += line
                
                # Process any remaining content
                if current_section:
                    messages = self._process_section(str(section_number), current_section)
                    all_messages.extend(messages)
                    
                    # Write to output if specified
                    if output_file:
                        if section_number > 0:  # Not the first section
                            output_file.write(self.ffmd.section_separator)
                        output_file.write(current_section)
        finally:
            # Close output file if opened
            if output_file:
                output_file.close()
        
        return all_messages
    
    def _split_into_sections(self, content: str) -> List[str]:
        """Split content into sections."""
        if not self.ffmd.section_separator:
            return [content]
        
        return content.split(self.ffmd.section_separator)
    
    def _process_section(self, section_number: str, section_content: str) -> List[Message]:
        """Process a section."""
        all_messages = []
        
        # Get section metadata
        section = self.ffmd.get_section(section_number)
        if not section:
            logger.warning(f"No metadata found for section {section_number}")
            return all_messages
        
        # Split into records
        records = self._split_into_records(section_content)
        
        # Process each record
        for record_number, record in enumerate(records):
            if self.ffmd.ignore_blank_rows and not record.strip():
                continue
            
            record_messages = self._process_record(section_number, record_number, record)
            all_messages.extend(record_messages)
        
        return all_messages
    
    def _split_into_records(self, section_content: str) -> List[str]:
        """Split section content into records."""
        if not self.ffmd.record_separator:
            return [section_content]
        
        return section_content.split(self.ffmd.record_separator)
    
    def _process_record(self, section_number: str, record_number: int, record: str) -> List[Message]:
        """Process a record."""
        all_messages = []
        
        # Get section metadata
        section = self.ffmd.get_section(section_number)
        if not section:
            return all_messages
        
        # Parse record into columns
        columns = self._parse_record(section_number, record)
        
        # Check column count
        if section.valid_column_counts and not section.is_valid_column_count(len(columns)):
            all_messages.append(Message(
                code="0001",
                section_number=section_number,
                column_number=-1,
                severity=MessageSeverity.ERROR.value,
                value=record,
                is_error=True,
                parameters={"{0}": str(len(columns)), "{1}": str(section.valid_column_counts)}
            ))
            return all_messages
        
        # Process each column
        for column_number, column_value in enumerate(columns):
            if column_number >= section.get_columns_count():
                break
            
            column_messages = self._process_column(section_number, record_number, column_number, column_value, record, columns)
            all_messages.extend(column_messages)
            
            # Update cross-record watchlists
            for global_rule in self.ffmd.global_rules:
                if global_rule.section_index == section_number and global_rule.column_index == column_number:
                    validator = self.crc_validators.get(global_rule.name)
                    if validator and hasattr(validator, "update_crc_watchlist"):
                        validator.update_crc_watchlist(global_rule, section_number, self.ffmd, columns)
        
        return all_messages
    
    def _parse_record(self, section_number: str, record: str) -> List[str]:
        """Parse a record into columns."""
        section = self.ffmd.get_section(section_number)
        if not section:
            return []
        
        # Get format
        format_code = section.section_format or self.ffmd.text_format_code
        
        if format_code == TextFormat.DELIMITED.value:
            # Parse delimited record
            return self._parse_delimited_record(record)
        elif format_code == TextFormat.FIXED_LENGTH.value:
            # Parse fixed-length record
            return self._parse_fixed_length_record(section_number, record)
        
        return []
    
    def _parse_delimited_record(self, record: str) -> List[str]:
        """Parse a delimited record."""
        if not self.ffmd.field_separator:
            return [record]
        
        # Handle text qualifier if specified
        if self.ffmd.text_qualifier:
            # This is a simplified implementation - a more robust one would handle escaped qualifiers
            result = []
            in_qualifier = False
            current = ""
            
            for char in record:
                if char == self.ffmd.text_qualifier:
                    in_qualifier = not in_qualifier
                    current += char
                elif char == self.ffmd.field_separator and not in_qualifier:
                    result.append(current)
                    current = ""
                else:
                    current += char
            
            if current:
                result.append(current)
            
            return result
        else:
            return record.split(self.ffmd.field_separator)
    
    def _parse_fixed_length_record(self, section_number: str, record: str) -> List[str]:
        """Parse a fixed-length record."""
        section = self.ffmd.get_section(section_number)
        if not section:
            return []
        
        # Get field lengths
        field_lengths = []
        for instruction in section.instructions or []:
            if instruction.name == "fl" and instruction.parameters:
                field_lengths = [int(length) for length in instruction.parameters]
                break
        
        if not field_lengths:
            return []
        
        # Parse record
        result = []
        start = 0
        
        for length in field_lengths:
            if start + length <= len(record):
                result.append(record[start:start + length])
            else:
                # Handle case where record is shorter than expected
                if self.ffmd.accept_trailing_white_space:
                    result.append(record[start:].ljust(length))
                else:
                    result.append(record[start:])
            
            start += length
        
        return result
    
    def _process_column(self, section_number: str, record_number: int, column_number: int, 
                       column_value: str, record: str, columns: List[str]) -> List[Message]:
        """Process a column."""
        all_messages = []
        
        # Get checks for this column
        checks = self.ffmd.get_column_checks(section_number, column_number)
        
        # Create validation context
        context = ValidationContext(
            column_index=column_number,
            section_index=section_number,
            record_index=record_number,
            record_number_within_section=record_number,
            record=record,
            columns=columns,
            file_props=self.ffmd
        )
        
        # Process each check
        for check in checks:
            # Skip if value is empty and check is optional
            if not column_value.strip() and check.is_optional:
                continue
            
            validator = self.validator_factory.get_validator(check.name)
            if validator:
                try:
                    result = validator.validate(check, column_value, context)
                    
                    # Check if the result has a message
                    if result and result.message:
                        all_messages.append(result.message)
                except Exception as e:
                    logger.error(f"Error validating {check.name} for section {section_number}, column {column_number}: {str(e)}")
                    all_messages.append(Message(
                        text=f"Error validating {check.name}: {str(e)}",
                        code="9999",
                        section_index=section_number,
                        column_index=column_number,
                        record_index=record_number,
                        severity=MessageSeverity.ERROR,
                        value=column_value,
                        is_error=True,
                        parameters={"{0}": str(e)}
                    ))
        
        return all_messages
    
    def _write_output_file(self, output_path: Path, content: str) -> None:
        """Write content to the output file."""
        try:
            with output_path.open('a', encoding=self.ffmd.encoding) as f:
                f.write(content)
        except Exception as e:
            raise ValidationError(f"Error writing to output file: {str(e)}")
    
    def _write_error_file(self, error_path: Path, messages: List[Message]) -> None:
        """Write the error file."""
        try:
            with error_path.open('w', encoding=self.ffmd.encoding) as f:
                for message in messages:
                    # Format based on error_format if specified
                    if self.ffmd.error_format:
                        line = self.ffmd.error_format
                        line = line.replace("{code}", message.code or "")
                        line = line.replace("{section}", message.section_index or "")
                        line = line.replace("{column}", str(message.column_index or ""))
                        line = line.replace("{severity}", str(message.severity) if message.severity else "")
                        line = line.replace("{value}", message.value or "")
                        line = line.replace("{alias}", message.column_alias or "")

                        # Replace parameters
                        if message.parameters:
                            for key, value in message.parameters.items():
                                line = line.replace(key, str(value))
                    else:
                        # Default format
                        line = f"{message.code or ''}|{message.section_index or ''}|{message.column_index or ''}|{message.severity or ''}|{message.value or ''}"

                    f.write(line + os.linesep)
        except Exception as e:
            raise ValidationError(f"Error writing error file: {str(e)}")
    
    def process_line_by_line(self, input_file: str, output_file: Optional[str] = None, error_file: Optional[str] = None) -> List[Message]:
        """
        Process a flat file line by line with minimal memory usage.
        This method is optimized for extremely large files.
        """
        all_messages = []
        
        # Convert to Path objects
        input_path = Path(input_file)
        output_path = Path(output_file) if output_file else None
        error_path = Path(error_file) if error_file else None
        
        # Check if input file exists
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Initialize state variables
        current_section = "0"
        current_record = ""
        record_number = 0
        section_record_number = 0
        
        # Open output file if specified
        output_file_handle = None
        if output_path:
            output_file_handle = output_path.open('w', encoding=self.ffmd.encoding)
        
        try:
            # Process the file line by line
            with input_path.open('r', encoding=self.ffmd.encoding) as f:
                for line in f:
                    # Check for section separator
                    if self.ffmd.section_separator and self.ffmd.section_separator in line:
                        # Process any remaining content in the current record
                        if current_record:
                            if not self.ffmd.ignore_blank_rows or current_record.strip():
                                messages = self._process_record(current_section, section_record_number, current_record)
                                all_messages.extend(messages)
                                section_record_number += 1
                                record_number += 1
                            
                            # Write to output if specified
                            if output_file_handle:
                                output_file_handle.write(current_record)
                                if not current_record.endswith(self.ffmd.record_separator):
                                    output_file_handle.write(self.ffmd.record_separator)
                        
                        # Move to the next section
                        current_section = str(int(current_section) + 1)
                        section_record_number = 0
                        current_record = ""
                        
                        # Write section separator to output if specified
                        if output_file_handle:
                            output_file_handle.write(self.ffmd.section_separator)
                        
                        # Process the rest of the line after the section separator
                        remaining = line.split(self.ffmd.section_separator, 1)[1]
                        if remaining:
                            current_record += remaining
                    
                    # Check for record separator
                    elif self.ffmd.record_separator and self.ffmd.record_separator in line:
                        parts = line.split(self.ffmd.record_separator)
                        
                        for i, part in enumerate(parts):
                            if i < len(parts) - 1:  # Not the last part
                                current_record += part
                                
                                # Process the complete record
                                if not self.ffmd.ignore_blank_rows or current_record.strip():
                                    messages = self._process_record(current_section, section_record_number, current_record)
                                    all_messages.extend(messages)
                                    section_record_number += 1
                                    record_number += 1
                                
                                # Write to output if specified
                                if output_file_handle:
                                    output_file_handle.write(current_record)
                                    output_file_handle.write(self.ffmd.record_separator)
                                
                                current_record = ""
                            else:  # Last part
                                current_record = part
                    else:
                        # Add line to current record
                        current_record += line
                
                # Process any remaining content
                if current_record:
                    if not self.ffmd.ignore_blank_rows or current_record.strip():
                        messages = self._process_record(current_section, section_record_number, current_record)
                        all_messages.extend(messages)
                    
                    # Write to output if specified
                    if output_file_handle:
                        output_file_handle.write(current_record)
        finally:
            # Close output file if opened
            if output_file_handle:
                output_file_handle.close()
        
        # Write error file if specified
        if error_path and all_messages:
            self._write_error_file(error_path, all_messages)
        
        return all_messages
    
    def process_file(self, file_path: str) -> bool:
        """Process a file and return True if no errors were found."""
        with open(file_path, 'r', encoding=self.ffmd.encoding) as f:
            content = f.read()
            return self.process_content(content)
    
    def process_content(self, content: str) -> bool:
        """Process content and return True if no errors were found."""
        self.errors = []
        self.warnings = []
        
        # Process the content
        # This is a simplified implementation
        for section_index, section in self.ffmd.sections.items():
            for column_index, rules in section.rules.items():
                for rule in rules:
                    validator = self.validator_factory.get_validator(rule.name)
                    if validator:
                        result = validator.validate(rule, content, ValidationContext(
                            column_index=column_index,
                            section_index=section_index,
                            record_index=0,
                            record_number_within_section=0,
                            record=content,
                            columns=[content],
                            file_props=self.ffmd
                        ))
                        if not result:
                            self.errors.append(f"Validation failed for rule {rule.name}")
        
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """Get the list of errors."""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Get the list of warnings."""
        return self.warnings 