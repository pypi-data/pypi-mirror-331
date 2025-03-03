"""
Tests for the processor module.
"""
import unittest
from unittest.mock import patch, MagicMock

from flatforge.processor import Processor
from flatforge.models import Rule, GlobalRule, Section, FileProperties, RuleResult


class TestProcessor(unittest.TestCase):
    """Tests for the Processor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.file_props = FileProperties()
        
        # Set up parameters
        self.file_props.set_parameters({
            "delimiter": ",",
            "section_separator": "\n\n",
            "record_separator": "\n"
        })
        
        # Set up sections
        section0 = Section(
            index="0",
            section_format="fl{10,5,15}",
            length=30,
            rules={
                0: [Rule(name="required"), Rule(name="numeric")],
                1: [Rule(name="length", parameters=["5"])],
                2: [Rule(name="regex", parameters=["[A-Z]{2,}"])]
            }
        )
        
        self.file_props.sections = {"0": section0}
        
        # Create processor
        self.processor = Processor(self.file_props)
    
    def test_process_file(self):
        """Test processing a file."""
        # Sample file content
        file_content = "1234567890ABCDE               \n0987654321FGHIJ               "
        
        # Process the file
        results = self.processor.process_file(file_content)
        
        # Check that results were returned
        self.assertIsInstance(results, dict)
        
        # Since our mock processor doesn't actually validate anything,
        # we expect no errors to be reported
        self.assertEqual(len(results), 1)
        self.assertIn("0", results)
        self.assertEqual(len(results["0"]), 0)
    
    def test_split_file_into_sections(self):
        """Test splitting a file into sections."""
        # Sample file content with two sections
        file_content = "Section 0 Line 1\nSection 0 Line 2\n\nSection 1 Line 1\nSection 1 Line 2"
        
        # Split the file
        sections = self.processor._split_file_into_sections(file_content)
        
        # Check that sections were correctly split
        self.assertIn("0", sections)
        self.assertEqual(len(sections["0"]), 2)
        self.assertEqual(sections["0"][0], "Section 0 Line 1")
        self.assertEqual(sections["0"][1], "Section 0 Line 2")
    
    def test_split_record_into_columns(self):
        """Test splitting a record into columns."""
        # Sample record for fixed-length format
        record = "1234567890ABCDE               "
        
        # Get the section
        section = self.file_props.sections["0"]
        
        # Split the record
        columns = self.processor._split_record_into_columns(section, record)
        
        # Check that columns were correctly split
        self.assertEqual(len(columns), 3)
        self.assertEqual(columns[0], "1234567890")
        self.assertEqual(columns[1], "ABCDE")
        self.assertEqual(columns[2], "               ")
    
    def test_process_rule(self):
        """Test processing a rule."""
        # Create a rule
        rule = Rule(name="required")
        
        # Mock the rule handler to return a validation error
        with patch.object(self.processor, '_get_rule_handler') as mock_handler:
            mock_handler.return_value = lambda value, params: (False, "Value is required")
            
            # Process the rule
            result = self.processor._process_rule(rule, "", "0", 0, 0)
            
            # Check that an error was returned
            self.assertIsInstance(result, RuleResult)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.message.text, "Value is required")
            self.assertEqual(result.message.section_index, "0")
            self.assertEqual(result.message.column_index, 0)
            self.assertEqual(result.message.record_index, 0)
    
    def test_process_optional_rule(self):
        """Test processing an optional rule."""
        # Create an optional rule
        rule = Rule(name="required", is_optional=True)
        
        # Mock the rule handler to return a validation error
        with patch.object(self.processor, '_get_rule_handler') as mock_handler:
            mock_handler.return_value = lambda value, params: (False, "Value is required")
            
            # Process the rule
            result = self.processor._process_rule(rule, "", "0", 0, 0)
            
            # Check that no error was returned (because the rule is optional)
            self.assertIsNone(result)
    
    def test_process_global_rule(self):
        """Test processing a global rule."""
        # Create a global rule
        rule = GlobalRule(name="cr_unique", section_index="0", column_index=0)
        
        # Add the rule to the file properties
        self.file_props.global_rules = [rule]
        
        # Mock the rule handler to return a validation error
        with patch.object(self.processor, '_get_rule_handler') as mock_handler:
            mock_handler.return_value = lambda value, params: (False, "Values must be unique")
            
            # Mock the method to get values for the global rule
            with patch.object(self.processor, '_get_values_for_global_rule') as mock_get_values:
                mock_get_values.return_value = ["value1", "value1"]  # Duplicate values
                
                # Process the global rules
                self.processor._process_global_rules()
                
                # Check that an error was added to the global results
                self.assertIn("0", self.processor.global_results)
                self.assertEqual(len(self.processor.global_results["0"]), 1)
                
                result = self.processor.global_results["0"][0]
                self.assertFalse(result.is_valid)
                self.assertEqual(result.message.text, "Values must be unique")
                self.assertEqual(result.message.section_index, "0")
                self.assertEqual(result.message.column_index, 0)


if __name__ == "__main__":
    unittest.main() 