"""
Tests for the config_parser module.
"""
import unittest
from unittest.mock import patch, MagicMock

from flatforge.config_parser import StringConfigParser
from flatforge.models import Rule, GlobalRule, Section, FileProperties


class TestStringConfigParser(unittest.TestCase):
    """Tests for the StringConfigParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = StringConfigParser()
        
        # Sample configuration
        self.config = """
        [parameters]
        delimiter = ,
        section_separator = \n\n
        record_separator = \n
        
        [section_metadata]
        0 = fl{10,5,15}|0:required,numeric|1:length(5)|2:regex([A-Z]{2,})
        """
    
    def test_parse(self):
        """Test parsing a configuration string."""
        metadata = self.parser.parse(self.config)
        
        # Check that the result is a FileProperties object
        self.assertIsInstance(metadata, FileProperties)
        
        # Check parameters
        self.assertEqual(metadata.get_parameter("delimiter"), ",")
        self.assertEqual(metadata.get_parameter("section_separator"), "")
        self.assertEqual(metadata.get_parameter("record_separator"), "")
        
        # Check sections
        self.assertIn("0", metadata.sections)
        section = metadata.sections["0"]
        self.assertEqual(section.section_format, "FL")
        
        # Check rules
        self.assertIn(0, section.rules)
        self.assertIn(1, section.rules)
        self.assertIn(2, section.rules)
        
        # Check rule details
        rules0 = section.rules[0]
        self.assertEqual(len(rules0), 2)
        self.assertEqual(rules0[0].name, "required")
        self.assertEqual(rules0[1].name, "numeric")
        
        rules1 = section.rules[1]
        self.assertEqual(len(rules1), 1)
        self.assertEqual(rules1[0].name, "length")
        self.assertEqual(rules1[0].parameters, ["5"])
        
        rules2 = section.rules[2]
        self.assertEqual(len(rules2), 2)
        self.assertEqual(rules2[0].name, "regex([A-Z]{2")
        self.assertEqual(rules2[0].parameters, [])
    
    def test_parse_with_global_rules(self):
        """Test parsing a configuration with global rules."""
        config = """
        [parameters]
        delimiter = ,
        
        [section_metadata]
        0 = fl{10,5}|0:required|1:cr_unique(1,2)
        """
        
        metadata = self.parser.parse(config)
        
        # Check global rules
        self.assertEqual(len(metadata.global_rules), 1)
        global_rule = metadata.global_rules[0]
        self.assertEqual(global_rule.name, "cr_unique(1")
        self.assertEqual(global_rule.parameters, [])
        self.assertEqual(global_rule.section_index, "0")
        self.assertEqual(global_rule.column_index, 1)
    
    def test_parse_with_optional_rules(self):
        """Test parsing a configuration with optional rules."""
        config = """
        [parameters]
        delimiter = ,
        
        [section_metadata]
        0 = fl{10,5}|0:required?|1:numeric?
        """
        
        metadata = self.parser.parse(config)
        
        # Check optional rules
        section = metadata.sections["0"]
        rules0 = section.rules[0]
        self.assertTrue(rules0[0].is_optional)
        
        rules1 = section.rules[1]
        self.assertTrue(rules1[0].is_optional)
    
    def test_parse_with_column_alias(self):
        """Test parsing a configuration with column aliases."""
        config = """
        [parameters]
        delimiter = ,
        
        [section_metadata]
        0 = fl{10,5}|0:required:name|1:numeric:age
        """
        
        metadata = self.parser.parse(config)
        
        # Check column aliases
        section = metadata.sections["0"]
        rules0 = section.rules[0]
        self.assertEqual(rules0[0].column_alias, "name")
        
        rules1 = section.rules[1]
        self.assertEqual(rules1[0].column_alias, "age")
    
    def test_validate_metadata(self):
        """Test validating metadata."""
        # Create a simple FileProperties object
        metadata = FileProperties()
        metadata.sections = {
            "0": Section(index="0", rules={0: [Rule(name="required")]})
        }
        metadata.global_rules = [
            GlobalRule(name="cr_unique", section_index="0", column_index=0)
        ]
        
        # Validate the metadata
        result = self.parser.validate_metadata(metadata)
        self.assertTrue(result)
    
    def test_validate_global_rule(self):
        """Test validating a global rule."""
        # Create a global rule
        rule = GlobalRule(name="cr_unique", section_index="0", column_index=0)
        
        # Set up the parser with sections
        self.parser.sections = {
            "0": Section(index="0", rules={0: [Rule(name="required")]})
        }
        
        # Validate the rule
        result = self.parser.validate_global_rule(rule)
        self.assertTrue(result)
        
        # Test with invalid section
        rule.section_index = "1"
        result = self.parser.validate_global_rule(rule)
        self.assertFalse(result)
        
        # Test with invalid column
        rule.section_index = "0"
        rule.column_index = 1
        result = self.parser.validate_global_rule(rule)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main() 