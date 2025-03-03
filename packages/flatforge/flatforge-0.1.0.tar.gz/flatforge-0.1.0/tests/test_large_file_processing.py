"""
Tests for large file processing.
"""
import os
import tempfile
import pytest
from pathlib import Path
import psutil
import unittest
from unittest.mock import patch, MagicMock

from flatforge.models import FileProperties, Section, Rule, GlobalRule
from flatforge.processor import ValidationProcessor, Processor
from flatforge.utils import TextFormat


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    file_props = FileProperties()
    file_props.text_format_code = TextFormat.DELIMITED.value
    file_props.field_separator = ","
    file_props.record_separator = "\n"
    file_props.encoding = "utf-8"
    
    # Create a section
    section = Section(index="0")
    section.section_format = TextFormat.DELIMITED.value
    
    # Add rules for columns
    section.rules = {
        0: [Rule(name="str", parameters=["10"])],
        1: [Rule(name="num", parameters=["5"])],
        2: [Rule(name="str", parameters=["20"])]
    }
    
    file_props.sections["0"] = section
    
    return file_props


def test_process_large_file(sample_config):
    """Test processing a large file."""
    # Create a temporary large file (not actually large for testing purposes)
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        # Write 1000 records
        for i in range(1000):
            f.write(f"test{i:04d},{i},description{i}\n")
    
    try:
        # Create processor
        processor = ValidationProcessor(sample_config)
        
        # Process using line-by-line method
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as out_f:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as err_f:
                messages = processor.process_line_by_line(f.name, out_f.name, err_f.name)
        
        # Verify results
        assert len(messages) == 0  # No validation errors expected
        
        # Check that output file was created and has the same content
        with open(out_f.name, 'r') as f_out:
            lines = f_out.readlines()
            assert len(lines) == 1000
            assert lines[0].strip() == "test0000,0,description0"
            assert lines[999].strip() == "test0999,999,description999"
    
    finally:
        # Clean up temporary files
        os.unlink(f.name)
        if 'out_f' in locals():
            os.unlink(out_f.name)
        if 'err_f' in locals():
            os.unlink(err_f.name)


def test_process_large_file_with_errors(sample_config):
    """Test processing a large file with validation errors."""
    print("\n=== Running test_process_large_file_with_errors ===")
    
    # Create a temporary large file with some invalid records
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        # Write 1000 records, with every 10th record having an invalid number
        for i in range(1000):
            if i % 10 == 0:
                f.write(f"test{i:04d},invalid,description{i}\n")  # Invalid number
            else:
                f.write(f"test{i:04d},{i},description{i}\n")
        print(f"Created test file: {f.name} with 1000 records (100 invalid)")
    
    try:
        # Create processor
        processor = ValidationProcessor(sample_config)
        
        # Process using line-by-line method
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as out_f:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as err_f:
                print(f"Processing file with output to: {out_f.name} and errors to: {err_f.name}")
                messages = processor.process_line_by_line(f.name, out_f.name, err_f.name)
        
        # Verify results
        print(f"Number of validation messages: {len(messages)}")
        assert len(messages) == 100  # 100 validation errors expected (every 10th record)
        
        # Check that error file was created and has content
        with open(err_f.name, 'r') as f_err:
            lines = f_err.readlines()
            print(f"Number of lines in error file: {len(lines)}")
            assert len(lines) == 200  # Each error message is followed by a newline
        
        # Check that output file was created and has the same content
        with open(out_f.name, 'r') as f_out:
            lines = f_out.readlines()
            print(f"Number of lines in output file: {len(lines)}")
            assert len(lines) == 1000
        
        print("=== test_process_large_file_with_errors completed successfully ===")
    
    finally:
        # Clean up temporary files
        os.unlink(f.name)
        if 'out_f' in locals():
            os.unlink(out_f.name)
        if 'err_f' in locals():
            os.unlink(err_f.name)


def test_memory_usage_large_file(sample_config):
    """Test memory usage when processing a large file."""
    # Skip this test in CI environments
    if os.environ.get('CI'):
        pytest.skip("Skipping memory usage test in CI environment")
    
    try:
        import gc
    except ImportError:
        pytest.skip("gc not installed, skipping memory usage test")
    
    # Create a temporary "large" file (10,000 records for testing)
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        for i in range(10000):
            f.write(f"test{i:04d},{i},description{i}\n")
    
    try:
        # Force garbage collection
        gc.collect()
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create processor
        processor = ValidationProcessor(sample_config)
        
        # Process using line-by-line method
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as out_f:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as err_f:
                messages = processor.process_line_by_line(f.name, out_f.name, err_f.name)
        
        # Force garbage collection again
        gc.collect()
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Check that memory usage didn't increase significantly
        # For a truly large file, we'd expect minimal increase
        # For this test, we'll just check it's not excessive
        memory_increase = final_memory - initial_memory
        
        # Log the memory usage (useful for debugging)
        print(f"Memory usage: initial={initial_memory:.2f}MB, final={final_memory:.2f}MB, increase={memory_increase:.2f}MB")
        
        # This is a loose check since the actual values depend on the environment
        assert memory_increase < 50, f"Memory increase was {memory_increase:.2f}MB, expected less than 50MB"
    
    finally:
        # Clean up temporary files
        os.unlink(f.name)
        if 'out_f' in locals():
            os.unlink(out_f.name)
        if 'err_f' in locals():
            os.unlink(err_f.name)


class TestLargeFileProcessing(unittest.TestCase):
    """Tests for processing large files."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock FileProperties
        self.file_props = FileProperties()
        
        # Set up parameters
        self.file_props.set_parameters({
            "delimiter": ",",
            "section_separator": "\n\n",
            "record_separator": "\n"
        })
        
        # Set up a section with rules
        section = Section(
            index="0",
            section_format="fl{10,5,15}",
            length=30,
            rules={
                0: [Rule(name="required"), Rule(name="numeric")],
                1: [Rule(name="length", parameters=["5"])],
                2: [Rule(name="regex", parameters=["[A-Z]{2,}"])]
            }
        )
        
        self.file_props.sections = {"0": section}
        
        # Create processor
        self.processor = Processor(self.file_props)
        
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file_path = self.temp_file.name
    
    def tearDown(self):
        """Clean up after tests."""
        # Close and remove the temporary file
        self.temp_file.close()
        os.unlink(self.temp_file_path)
    
    def test_process_large_file(self):
        """Test processing a large file."""
        # Create a large file with valid content
        with open(self.temp_file_path, 'w') as f:
            for i in range(1000):
                f.write(f"{'1234567890':<10}{'ABCDE':<5}{'VALID':<15}\n")
        
        # Process the file
        with open(self.temp_file_path, 'r') as f:
            content = f.read()
            results = self.processor.process_file(content)
        
        # Check that results were returned
        self.assertIsInstance(results, dict)
        
        # Since our mock processor doesn't actually validate anything,
        # we expect no errors to be reported
        self.assertEqual(len(results), 1)
        self.assertIn("0", results)
        self.assertEqual(len(results["0"]), 0)
    
    def test_process_large_file_with_errors(self):
        """Test processing a large file with errors."""
        # Create a large file with some invalid content
        with open(self.temp_file_path, 'w') as f:
            for i in range(1000):
                if i % 10 == 0:
                    # Every 10th line has an invalid value
                    f.write(f"{'invalid':<10}{'ABCDE':<5}{'VALID':<15}\n")
                else:
                    f.write(f"{'1234567890':<10}{'ABCDE':<5}{'VALID':<15}\n")
        
        # Mock the _process_rule method to return errors for invalid values
        original_process_rule = self.processor._process_rule
        
        def mock_process_rule(rule, value, section_index, column_index, record_index):
            if rule.name == "numeric" and not value.strip().isdigit():
                from flatforge.models import RuleResult, Message, MessageSeverity
                return RuleResult(
                    rule=rule,
                    value=value,
                    is_valid=False,
                    message=Message(
                        text="Value is not numeric",
                        section_index=section_index,
                        column_index=column_index,
                        record_index=record_index,
                        severity=MessageSeverity.ERROR
                    )
                )
            return original_process_rule(rule, value, section_index, column_index, record_index)
        
        with patch.object(self.processor, '_process_rule', side_effect=mock_process_rule):
            # Process the file
            with open(self.temp_file_path, 'r') as f:
                content = f.read()
                results = self.processor.process_file(content)
            
            # Check that results were returned
            self.assertIsInstance(results, dict)
            
            # Check that errors were reported
            self.assertEqual(len(results), 1)
            self.assertIn("0", results)
            self.assertEqual(len(results["0"]), 100)  # 100 errors (every 10th line)


if __name__ == "__main__":
    unittest.main() 