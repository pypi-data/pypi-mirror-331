"""
Tests for the processors.
"""
import os
import tempfile
import unittest
import pytest
from io import StringIO
from unittest.mock import MagicMock, patch, mock_open

from flatforge.models import FileProperties, Section, Rule
from flatforge.processors import (
    ProcessorAdapter, PropertiesToMapCopier, RecordCounter,
    TextAppender, BaseFormatConverter
)
from flatforge.processor_factory import ProcessorFactory
from flatforge.utils import TextFormat
from flatforge.processor import ValidationProcessor, ValidatorFactory


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    file_props = FileProperties()
    file_props.text_format_code = TextFormat.DELIMITED.value
    file_props.field_separator = "="
    file_props.record_separator = "\n"
    file_props.encoding = "utf-8"
    
    return file_props


def test_properties_to_map_copier(sample_config):
    """Test the PropertiesToMapCopier processor."""
    # Create processor
    processor = PropertiesToMapCopier()
    processor.initialize(sample_config, -1)
    
    # Process some records
    processor.process_record("key1=value1", "0", 0, 0, sample_config, False)
    processor.process_record("key2=value2", "0", 1, 1, sample_config, False)
    processor.process_record("# This is a comment", "0", 2, 2, sample_config, False)
    processor.process_record("key3=value3", "0", 3, 3, sample_config, False)
    processor.process_record("key1=value4", "0", 4, 4, sample_config, False)  # Duplicate key
    
    # Finalize processing
    processor.finalize("0", 5, sample_config, False)
    
    # Check results
    payload = processor.get_payload()
    assert len(payload) == 3
    assert payload["key1"] == "value4"  # Last value for duplicate key
    assert payload["key2"] == "value2"
    assert payload["key3"] == "value3"
    assert processor.previous_key == "key1"  # Duplicate key detected


def test_record_counter(sample_config):
    """Test the RecordCounter processor."""
    # Create processor
    processor = RecordCounter()
    processor.initialize(sample_config, -1)
    
    # Process some records
    processor.process_record("record1", "0", 0, 0, sample_config, False)
    processor.process_record("record2", "0", 1, 1, sample_config, False)
    processor.process_record("", "0", 2, 2, sample_config, False)  # Blank record
    processor.process_record("record3", "0", 3, 3, sample_config, False)
    
    # Finalize processing
    processor.finalize("0", 4, sample_config, False)
    
    # Check results
    assert processor.get_record_count() == 4  # All records are counted


def test_text_appender(sample_config):
    """Test the TextAppender processor."""
    # Create processor
    processor = TextAppender()
    processor.initialize(sample_config, -1)
    
    # Process some records
    processor.process_record("line1", "0", 0, 0, sample_config, False)
    processor.process_record("line2", "0", 1, 1, sample_config, False)
    processor.process_record("line3", "0", 2, 2, sample_config, False)
    
    # Finalize processing
    processor.finalize("0", 3, sample_config, False)
    
    # Check results
    assert processor.get_file_contents() == "line1line2line3"
    assert processor.get_payload() == "line1line2line3"


def test_base_format_converter(sample_config):
    """Test the BaseFormatConverter processor."""
    print("\n=== Running test_base_format_converter ===")
    
    # Create output stream
    out_stream = StringIO()
    error_stream = StringIO()
    
    # Create processor
    processor = BaseFormatConverter(out_stream, error_stream)
    
    # Directly call the _write_to_stream method
    processor._write_to_stream(out_stream, "field1field2\n", "utf-8")
    processor._write_to_stream(out_stream, "field3field4\n", "utf-8")
    
    # Check results
    out_content = out_stream.getvalue()
    print(f"Output content: {out_content}")
    assert "field1field2" in out_content
    assert "field3field4" in out_content
    
    print("=== test_base_format_converter completed successfully ===")


def test_processor_factory(sample_config):
    """Test the ProcessorFactory."""
    # Test getting each processor type
    properties_to_map_copier = ProcessorFactory.get_processor("properties_to_map_copier", sample_config)
    assert properties_to_map_copier is not None
    assert isinstance(properties_to_map_copier, PropertiesToMapCopier)
    
    record_counter = ProcessorFactory.get_processor("record_counter", sample_config)
    assert record_counter is not None
    assert isinstance(record_counter, RecordCounter)
    
    text_appender = ProcessorFactory.get_processor("text_appender", sample_config)
    assert text_appender is not None
    assert isinstance(text_appender, TextAppender)
    
    base_format_converter = ProcessorFactory.get_processor("format_converter", sample_config)
    assert base_format_converter is not None
    assert isinstance(base_format_converter, BaseFormatConverter)
    
    # Test getting a non-existent processor type
    non_existent = ProcessorFactory.get_processor("non_existent", sample_config)
    assert non_existent is None


class TestValidationProcessor(unittest.TestCase):
    """Tests for the ValidationProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock FileProperties
        self.file_props = FileProperties()
        
        # Create a mock validator factory
        self.validator_factory = MagicMock(spec=ValidatorFactory)
        
        # Create the processor
        self.processor = ValidationProcessor(self.file_props, self.validator_factory)
    
    def test_init(self):
        """Test initialization of ValidationProcessor."""
        self.assertEqual(self.processor.ffmd, self.file_props)
        self.assertEqual(self.processor.validator_factory, self.validator_factory)
        self.assertEqual(self.processor.buffer_size, 8192)  # Default buffer size
    
    def test_custom_buffer_size(self):
        """Test initialization with custom buffer size."""
        processor = ValidationProcessor(self.file_props, self.validator_factory, buffer_size=4096)
        self.assertEqual(processor.buffer_size, 4096)
    
    def test_process_file(self):
        """Test processing a file."""
        # Mock the process_content method
        with patch.object(self.processor, 'process_content') as mock_process:
            mock_process.return_value = True
            
            # Mock the open function
            with patch('builtins.open', mock_open(read_data='test data')):
                # Process a file
                result = self.processor.process_file("test_file.txt")
                
                # Check that process_content was called
                mock_process.assert_called_once()
                
                # Check the result
                self.assertTrue(result)
    
    def test_process_content(self):
        """Test processing content."""
        # Set up a simple file properties with a section and rules
        section = Section(
            index="0",
            section_format="fl{10,5}",
            rules={0: [Rule(name="required")]}
        )
        self.file_props.sections = {"0": section}
        
        # Mock the validator factory to return a validator that always succeeds
        mock_validator = MagicMock()
        mock_validator.validate.return_value = True
        self.validator_factory.get_validator.return_value = mock_validator
        
        # Process some content
        content = "1234567890ABCDE"
        result = self.processor.process_content(content)
        
        # Check the result
        self.assertTrue(result)
    
    def test_process_content_with_errors(self):
        """Test processing content with errors."""
        # Set up a simple file properties with a section and rules
        section = Section(
            index="0",
            section_format="fl{10,5}",
            rules={0: [Rule(name="required")]}
        )
        self.file_props.sections = {"0": section}
        
        # Mock the validator factory to return a validator that fails
        mock_validator = MagicMock()
        mock_validator.validate.return_value = False
        self.validator_factory.get_validator.return_value = mock_validator
        
        # Process some content
        content = "1234567890ABCDE"
        result = self.processor.process_content(content)
        
        # Check the result
        self.assertFalse(result)
    
    def test_get_errors(self):
        """Test getting errors."""
        # Add some errors
        self.processor.errors = ["Error 1", "Error 2"]
        
        # Get the errors
        errors = self.processor.get_errors()
        
        # Check the errors
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0], "Error 1")
        self.assertEqual(errors[1], "Error 2")
    
    def test_get_warnings(self):
        """Test getting warnings."""
        # Add some warnings
        self.processor.warnings = ["Warning 1", "Warning 2"]
        
        # Get the warnings
        warnings = self.processor.get_warnings()
        
        # Check the warnings
        self.assertEqual(len(warnings), 2)
        self.assertEqual(warnings[0], "Warning 1")
        self.assertEqual(warnings[1], "Warning 2")


if __name__ == "__main__":
    unittest.main() 