"""
Tests for the yaml_config_parser module.
"""
import unittest
import yaml
from flatforge.yaml_config_parser import YamlConfigParser
from flatforge.models import Rule, GlobalRule, Section, FileProperties


class TestYamlConfigParser(unittest.TestCase):
    """Tests for the YamlConfigParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = YamlConfigParser()
    
    def test_parse_simple_config(self):
        """Test parsing a simple YAML configuration."""
        config = """
        delimiter: ','
        encoding: utf-8
        section_metadata:
          '1':
            format:
              type: FL
              lengths: [10, 5, 15]
          '2':
            format:
              type: DEL
        """
        
        metadata = self.parser.parse(config)
        
        self.assertIsInstance(metadata, FileProperties)
        self.assertEqual(metadata.get_parameter("delimiter"), ",")
        self.assertEqual(metadata.get_parameter("encoding"), "utf-8")
        self.assertEqual(len(metadata.sections), 2)
        self.assertIn("1", metadata.sections)
        self.assertIn("2", metadata.sections)
        
        section1 = metadata.sections["1"]
        self.assertEqual(section1.section_format, "fl{10,5,15}")
        self.assertEqual(section1.length, 30)  # 10 + 5 + 15
        
        section2 = metadata.sections["2"]
        self.assertEqual(section2.section_format, "del")
    
    def test_parse_config_with_rules(self):
        """Test parsing a YAML configuration with rules."""
        config = """
        delimiter: ','
        encoding: utf-8
        section_metadata:
          '1':
            format:
              type: FL
              lengths: [10, 5, 15]
            columns:
              - rules:
                - name: required
                - name: length
                  parameters: ['10']
              - rules:
                - name: numeric
              - rules:
                - name: in
                  parameters: ['A', 'B', 'C']
          '2':
            format:
              type: DEL
            columns:
              - rules:
                - name: required
              - rules:
                - name: date
                  parameters: ['%Y-%m-%d']
        """
        
        metadata = self.parser.parse(config)
        
        self.assertIsInstance(metadata, FileProperties)
        self.assertEqual(len(metadata.sections), 2)
        
        # Check section 1
        section1 = metadata.sections["1"]
        self.assertEqual(section1.section_format, "fl{10,5,15}")
        self.assertEqual(section1.length, 30)
        
        # Check rules for column 0 in section 1
        self.assertIn(0, section1.rules)
        col0_rules = section1.rules[0]
        self.assertEqual(len(col0_rules), 2)
        self.assertEqual(col0_rules[0].name, "required")
        self.assertEqual(col0_rules[1].name, "length")
        self.assertEqual(col0_rules[1].parameters, ["10"])
        
        # Check rules for column 1 in section 1
        self.assertIn(1, section1.rules)
        col1_rules = section1.rules[1]
        self.assertEqual(len(col1_rules), 1)
        self.assertEqual(col1_rules[0].name, "numeric")
        
        # Check rules for column 2 in section 1
        self.assertIn(2, section1.rules)
        col2_rules = section1.rules[2]
        self.assertEqual(len(col2_rules), 1)
        self.assertEqual(col2_rules[0].name, "in")
        self.assertEqual(col2_rules[0].parameters, ["A", "B", "C"])
        
        # Check section 2
        section2 = metadata.sections["2"]
        self.assertEqual(section2.section_format, "del")
        
        # Check rules for column 0 in section 2
        self.assertIn(0, section2.rules)
        col0_rules = section2.rules[0]
        self.assertEqual(len(col0_rules), 1)
        self.assertEqual(col0_rules[0].name, "required")
        
        # Check rules for column 1 in section 2
        self.assertIn(1, section2.rules)
        col1_rules = section2.rules[1]
        self.assertEqual(len(col1_rules), 1)
        self.assertEqual(col1_rules[0].name, "date")
        self.assertEqual(col1_rules[0].parameters, ["%Y-%m-%d"])
    
    def test_parse_config_with_global_rules(self):
        """Test parsing a YAML configuration with global rules."""
        config = """
        delimiter: ','
        encoding: utf-8
        section_metadata:
          '1':
            format:
              type: FL
              lengths: [10, 5, 15]
            columns:
              - rules:
                - name: required
                - name: cr_unique
              - rules:
                - name: numeric
              - rules:
                - name: in
                  parameters: ['A', 'B', 'C']
        """
        
        metadata = self.parser.parse(config)
        
        self.assertIsInstance(metadata, FileProperties)
        self.assertEqual(len(metadata.sections), 1)
        
        # Check global rules
        self.assertEqual(len(metadata.global_rules), 1)
        global_rule = metadata.global_rules[0]
        self.assertIsInstance(global_rule, GlobalRule)
        self.assertEqual(global_rule.name, "cr_unique")
        self.assertEqual(global_rule.section_index, "1")
        self.assertEqual(global_rule.column_index, 0)
    
    def test_parse_config_with_instructions(self):
        """Test parsing a YAML configuration with instructions."""
        config = """
        delimiter: ','
        encoding: utf-8
        section_metadata:
          '1':
            format:
              type: FL
              lengths: [10, 5, 15]
            instructions:
              - name: fl
                parameters: ['10', '5', '15']
              - name: required
            columns:
              - rules:
                - name: required
        """
        
        metadata = self.parser.parse(config)
        
        self.assertIsInstance(metadata, FileProperties)
        self.assertEqual(len(metadata.sections), 1)
        
        # Check instructions
        section = metadata.sections["1"]
        self.assertEqual(len(section.instructions), 2)
        self.assertEqual(section.instructions[0].name, "fl")
        self.assertEqual(section.instructions[0].parameters, ["10", "5", "15"])
        self.assertEqual(section.instructions[1].name, "required")
    
    def test_parse_config_with_dict(self):
        """Test parsing a YAML configuration from a dictionary."""
        config_dict = {
            "delimiter": ",",
            "encoding": "utf-8",
            "section_metadata": {
                "1": {
                    "format": {
                        "type": "FL",
                        "lengths": [10, 5, 15]
                    },
                    "columns": [
                        {
                            "rules": [
                                {"name": "required"},
                                {"name": "length", "parameters": ["10"]}
                            ]
                        }
                    ]
                }
            }
        }
        
        metadata = self.parser.parse(config_dict)
        
        self.assertIsInstance(metadata, FileProperties)
        self.assertEqual(metadata.get_parameter("delimiter"), ",")
        self.assertEqual(metadata.get_parameter("encoding"), "utf-8")
        self.assertEqual(len(metadata.sections), 1)
        
        section = metadata.sections["1"]
        self.assertEqual(section.section_format, "fl{10,5,15}")
        self.assertEqual(section.length, 30)
        
        self.assertIn(0, section.rules)
        col0_rules = section.rules[0]
        self.assertEqual(len(col0_rules), 2)
        self.assertEqual(col0_rules[0].name, "required")
        self.assertEqual(col0_rules[1].name, "length")
        self.assertEqual(col0_rules[1].parameters, ["10"])
    
    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML."""
        config = """
        delimiter: ','
        encoding: 'utf-8
        """
        
        with self.assertRaises(ValueError):
            self.parser.parse(config)
    
    def test_parse_invalid_config_type(self):
        """Test parsing an invalid configuration type."""
        config = 123  # Not a string or dictionary
        
        with self.assertRaises(ValueError):
            self.parser.parse(config)
    
    def test_parse_invalid_section_format(self):
        """Test parsing an invalid section format."""
        config = """
        section_metadata:
          '1': 123  # Not a string or dictionary
        """
        
        with self.assertRaises(ValueError):
            self.parser.parse(config)


if __name__ == "__main__":
    unittest.main() 