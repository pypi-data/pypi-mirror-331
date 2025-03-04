"""
Additional processors for FlatForge.

This module contains various processors for handling flat files:
- ProcessorAdapter: Base class for all processors
- PropertiesToMapCopier: Copies properties from a file to a dictionary
- RecordCounter: Counts records in a file
- TextAppender: Appends text from a file to a buffer
- BaseFormatConverter: Converts between file formats
"""
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, TextIO, BinaryIO
from pathlib import Path

from .models import FileProperties, RuleResult, Message, MessageSeverity
from .utils import StringUtils, ValidationError, ParserError

# Set up logging
logger = logging.getLogger(__name__)


class ProcessorAdapter(ABC):
    """Base class for processors."""
    
    def __init__(self):
        """Initialize the processor."""
        self.context = {}
        self.payload = {}
        self.ffmd = None
        self.total_records = -1
        self.out_stream = None
        self.error_stream = None
        self.buffer_size = 8192
    
    def initialize(self, file_props: FileProperties, total_records: int) -> None:
        """Initialize the processor."""
        self.ffmd = file_props
        self.total_records = total_records
    
    @abstractmethod
    def process_record(self, record: str, section_index: str, record_index: int, 
                      record_number_within_section: int, file_props: FileProperties,
                      is_markup: bool) -> Optional[RuleResult]:
        """Process a record."""
        pass
    
    def finalize(self, section_index: str, record_index: int, 
                file_props: FileProperties, is_processor_errors: bool) -> Optional[RuleResult]:
        """Finalize processing."""
        return None
    
    def terminate(self, section_count: int, record_count: int, 
                 file_props: FileProperties, is_processor_errors: bool) -> Optional[RuleResult]:
        """Terminate processing - calls finalize with the last section index."""
        section_index = str(section_count - 1) if section_count > 0 else "0"
        return self.finalize(section_index, record_count, file_props, is_processor_errors)
    
    def get_payload(self) -> Any:
        """Get the processor payload."""
        return self.payload
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set the processor context."""
        self.context = context
    
    def get_context(self) -> Dict[str, Any]:
        """Get the processor context."""
        return self.context
    
    def set_out_stream(self, out_stream: Optional[Union[TextIO, BinaryIO]]) -> None:
        """Set the output stream.
        
        Args:
            out_stream: The output stream
        """
        self.out_stream = out_stream
    
    def set_error_stream(self, error_stream: Optional[Union[TextIO, BinaryIO]]) -> None:
        """Set the error stream.
        
        Args:
            error_stream: The error stream
        """
        self.error_stream = error_stream
    
    def set_buffer_size(self, buffer_size: int) -> None:
        """Set the buffer size.
        
        Args:
            buffer_size: The buffer size in bytes
        """
        self.buffer_size = buffer_size
    
    def parse_record(self, record: str, section_index: str, file_props: FileProperties) -> List[str]:
        """Parse a record into columns."""
        if is_blank(record):
            return []
        
        section = file_props.get_section(section_index)
        if not section:
            return []
        
        if section.section_format == TextFormat.FIXED_LENGTH.value:
            # Fixed length format
            columns = []
            start = 0
            
            for column_index in range(section.get_columns_count()):
                rules = section.get_rules(column_index)
                if rules and len(rules) > 0:
                    # Get the length from the first rule
                    length = int(rules[0].parameters[0]) if rules[0].parameters else 0
                    
                    # Extract the column value
                    if start < len(record):
                        end = min(start + length, len(record))
                        columns.append(record[start:end])
                        start = end
                    else:
                        columns.append("")
                else:
                    columns.append("")
            
            return columns
        else:
            # Delimited format
            field_separator = file_props.field_separator or ","
            text_qualifier = file_props.text_qualifier
            
            if text_qualifier:
                return StringUtils.split_with_qualifier(record, field_separator, False, text_qualifier)
            else:
                return StringUtils.split(record, field_separator, False)


class PropertiesToMapCopier(ProcessorAdapter):
    """Processor that copies properties from a file to a dictionary."""
    
    def __init__(self):
        """Initialize the processor."""
        super().__init__()
        self.previous_key = None
    
    def process_record(self, record: str, section_index: str, record_index: int, 
                      record_number_within_section: int, file_props: FileProperties,
                      is_markup: bool) -> Optional[RuleResult]:
        """Process a record."""
        # Skip comments
        if record.strip().startswith("#"):
            return None
        
        # Split into key-value pair
        pair = StringUtils.split(record, file_props.field_separator, False)
        
        # Store in payload if valid
        if len(pair) > 1:
            key = pair[0].strip()
            value = pair[1].strip()
            
            # Check for duplicate keys
            if key in self.payload:
                self.previous_key = key
                logger.debug(f"Duplicate key [{key}] at row {record_index}")
            
            self.payload[key] = value
        
        return None
    
    def finalize(self, section_index: str, record_index: int, 
                file_props: FileProperties, is_processor_errors: bool) -> Optional[RuleResult]:
        """Finalize processing."""
        logger.debug("")
        logger.debug(f"Processed {len(self.payload)} key/value pairs out of {record_index} lines in source file.")
        logger.debug("======================================================================")
        return None


class RecordCounter(ProcessorAdapter):
    """Processor that counts records in a file."""
    
    def __init__(self):
        """Initialize the processor."""
        super().__init__()
        self.record_count = 0
    
    def process_record(self, record: str, section_index: str, record_index: int, 
                      record_number_within_section: int, file_props: FileProperties,
                      is_markup: bool) -> Optional[RuleResult]:
        """Process a record."""
        # Check if record is blank
        if record.strip() == "":
            if not file_props.ignore_blank_rows:
                self.record_count += 1
        else:
            self.record_count += 1
        
        return None
    
    def get_record_count(self) -> int:
        """Get the record count."""
        return self.record_count
    
    def get_payload(self) -> Any:
        """Get the processor payload."""
        return self.record_count
    
    def finalize(self, section_index: str, record_index: int, 
                file_props: FileProperties, is_processor_errors: bool) -> Optional[RuleResult]:
        """Finalize processing."""
        # Write to output stream if available
        if self.out_stream:
            try:
                self.out_stream.write(f"Total records: {self.record_count}\n")
                self.out_stream.flush()
            except Exception as e:
                logger.error(f"Error writing to output stream: {str(e)}")
        return None


class TextAppender(ProcessorAdapter):
    """Processor that appends text from a file to a buffer."""
    
    def __init__(self):
        """Initialize the processor."""
        super().__init__()
        self.file_contents = []
    
    def process_record(self, record: str, section_index: str, record_index: int, 
                      record_number_within_section: int, file_props: FileProperties,
                      is_markup: bool) -> Optional[RuleResult]:
        """Process a record."""
        self.file_contents.append(record)
        return None
    
    def get_file_contents(self) -> str:
        """Get the file contents."""
        return "".join(self.file_contents)
    
    def get_payload(self) -> Any:
        """Get the processor payload."""
        return self.get_file_contents()
    
    def finalize(self, section_index: str, record_index: int, 
                file_props: FileProperties, is_processor_errors: bool) -> Optional[RuleResult]:
        """Finalize processing."""
        # Write to output stream if available
        if self.out_stream:
            try:
                self.out_stream.write(self.get_file_contents())
                self.out_stream.flush()
            except Exception as e:
                logger.error(f"Error writing to output stream: {str(e)}")
        return None


class BaseFormatConverter(ProcessorAdapter):
    """Processor that converts between file formats."""
    
    def __init__(self, out_stream: Optional[Union[TextIO, BinaryIO]] = None, 
                error_stream: Optional[Union[TextIO, BinaryIO]] = None):
        """Initialize the processor."""
        super().__init__()
        self.out = out_stream
        self.exception = error_stream
        self.target = None
    
    def process_record(self, record: str, section_index: str, record_index: int, 
                      record_number_within_section: int, file_props: FileProperties,
                      is_markup: bool) -> Optional[RuleResult]:
        """Process a record."""
        record_result = RuleResult()
        
        try:
            # Parse the record
            columns = self.parse_record(record, section_index, file_props)
            
            # Write to output stream if we have at least 2 columns
            if len(columns) > 1:
                self._write_to_stream(self.out, f"{columns[0]}{columns[1]}{file_props.record_separator}", file_props.encoding)
        
        except ParserError as e:
            # Add error message
            record_result.add_message(Message(
                code=e.error_code,
                section_number=section_index,
                column_number=-2,
                severity=MessageSeverity.ERROR.value,
                value=record,
                is_error=True,
                column_alias="record",
                parameters=e.values
            ))
        except Exception as e:
            logger.error(f"Error processing record: {str(e)}")
        
        return record_result
    
    def _write_to_stream(self, stream: Optional[Union[TextIO, BinaryIO]], 
                        data: str, encoding: str) -> None:
        """Write data to a stream."""
        if stream is not None:
            try:
                if hasattr(stream, 'write'):
                    # TextIO
                    stream.write(data)
                else:
                    # BinaryIO
                    stream.write(data.encode(encoding))
            except Exception as e:
                logger.error(f"Error writing to stream: {str(e)}")
    
    def finalize(self, section_index: str, record_index: int, 
                file_props: FileProperties, is_processor_errors: bool) -> Optional[RuleResult]:
        """Finalize processing."""
        return None 