"""
Tests for the configuration parser factory.
"""
import unittest

from flatforge.config_parser_factory import ConfigParserFactory
from flatforge.config_parser import StringConfigParser
from flatforge.yaml_config_parser import YamlConfigParser


class TestConfigParserFactory(unittest.TestCase):
    """Test cases for the ConfigParserFactory."""
    
    def test_get_config_parser_txt(self):
        """Test getting a StringConfigParser for a .txt file."""
        parser = ConfigParserFactory.get_config_parser("config.txt")
        self.assertIsInstance(parser, StringConfigParser)
    
    def test_get_config_parser_yaml(self):
        """Test getting a YamlConfigParser for a .yaml file."""
        parser = ConfigParserFactory.get_config_parser("config.yaml")
        self.assertIsInstance(parser, YamlConfigParser)
    
    def test_get_config_parser_yml(self):
        """Test getting a YamlConfigParser for a .yml file."""
        parser = ConfigParserFactory.get_config_parser("config.yml")
        self.assertIsInstance(parser, YamlConfigParser)
    
    def test_get_config_parser_unsupported(self):
        """Test getting a parser for an unsupported file extension."""
        with self.assertRaises(ValueError):
            ConfigParserFactory.get_config_parser("config.json")
    
    def test_get_config_parser_by_type_text(self):
        """Test getting a StringConfigParser by type."""
        parser = ConfigParserFactory.get_config_parser_by_type("text")
        self.assertIsInstance(parser, StringConfigParser)
    
    def test_get_config_parser_by_type_yaml(self):
        """Test getting a YamlConfigParser by type."""
        parser = ConfigParserFactory.get_config_parser_by_type("yaml")
        self.assertIsInstance(parser, YamlConfigParser)
    
    def test_get_config_parser_by_type_unsupported(self):
        """Test getting a parser for an unsupported type."""
        with self.assertRaises(ValueError):
            ConfigParserFactory.get_config_parser_by_type("json")


if __name__ == '__main__':
    unittest.main() 