#!/usr/bin/env python
"""
Tests for the utils module.

Author: Akram Zaki (azpythonprojects@gmail.com)
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flatforge.utils import StringUtils, TextFormat, FlatFileError, ValidationError, ConfigurationError


class TestStringUtils(unittest.TestCase):
    """Tests for the StringUtils class."""

    def test_is_blank(self):
        """Test the is_blank method."""
        self.assertTrue(StringUtils.is_blank(None))
        self.assertTrue(StringUtils.is_blank(""))
        self.assertTrue(StringUtils.is_blank("  "))
        self.assertFalse(StringUtils.is_blank("test"))
        self.assertFalse(StringUtils.is_blank("  test  "))

    def test_split(self):
        """Test the split method."""
        # Test with default separator
        result = StringUtils.split("a,b,c", ",")
        self.assertEqual(result, ["a", "b", "c"])

        # Test with custom separator
        result = StringUtils.split("a|b|c", "|")
        self.assertEqual(result, ["a", "b", "c"])

        # Test with empty string
        result = StringUtils.split("", ",")
        self.assertEqual(result, [])

        # Test with None
        result = StringUtils.split(None, ",")
        self.assertEqual(result, [])

    def test_split_with_qualifier(self):
        """Test the split_with_qualifier method."""
        # Test with default separator and qualifier
        result = StringUtils.split_with_qualifier('a,"b,c",d', ",", False, '"')
        self.assertEqual(result, ["a", "\"b,c\"", "d"])

        # Test with custom separator and qualifier
        result = StringUtils.split_with_qualifier('a|"b|c"|d', "|", False, '"')
        self.assertEqual(result, ["a", "\"b|c\"", "d"])

        # Test with empty string
        result = StringUtils.split_with_qualifier("", ",")
        self.assertEqual(result, [])

        # Test with None
        result = StringUtils.split_with_qualifier(None, ",")
        self.assertEqual(result, [])

    def test_is_numeric(self):
        """Test is_numeric method."""
        self.assertTrue(StringUtils.is_numeric("123"))
        self.assertTrue(StringUtils.is_numeric("123.45"))
        self.assertTrue(StringUtils.is_numeric("-123"))
        self.assertTrue(StringUtils.is_numeric("-123.45"))
        
        self.assertFalse(StringUtils.is_numeric(""))
        self.assertFalse(StringUtils.is_numeric("abc"))
        self.assertFalse(StringUtils.is_numeric("123abc"))
        self.assertFalse(StringUtils.is_numeric("123.45.67"))
    
    def test_is_valid_date(self):
        """Test is_valid_date method."""
        self.assertTrue(StringUtils.is_valid_date("2023-01-01", "%Y-%m-%d"))
        self.assertTrue(StringUtils.is_valid_date("20230101", "%Y%m%d"))
        self.assertTrue(StringUtils.is_valid_date("01/01/2023", "%m/%d/%Y"))
        
        self.assertFalse(StringUtils.is_valid_date("", "%Y-%m-%d"))
        self.assertFalse(StringUtils.is_valid_date("2023-13-01", "%Y-%m-%d"))  # Invalid month
        self.assertFalse(StringUtils.is_valid_date("2023-01-32", "%Y-%m-%d"))  # Invalid day
        self.assertFalse(StringUtils.is_valid_date("2023-01-01", "%m/%d/%Y"))  # Wrong format
    
    def test_matches_regex(self):
        """Test matches_regex method."""
        self.assertTrue(StringUtils.matches_regex("abc123", r"[a-z]+\d+"))
        self.assertTrue(StringUtils.matches_regex("ABC", r"[A-Z]+"))
        self.assertTrue(StringUtils.matches_regex("123", r"\d+"))
        
        self.assertFalse(StringUtils.matches_regex("", r"[a-z]+"))
        self.assertFalse(StringUtils.matches_regex("abc", r"\d+"))
        self.assertFalse(StringUtils.matches_regex("ABC", r"[a-z]+"))
        
        # Test with invalid regex pattern
        self.assertFalse(StringUtils.matches_regex("abc", r"[a-z"))
    
    def test_prepare_escape_chars(self):
        """Test prepare_escape_chars method."""
        self.assertEqual(StringUtils.prepare_escape_chars("abc\\ndef"), "abc\ndef")
        self.assertEqual(StringUtils.prepare_escape_chars("abc\\tdef"), "abc\tdef")
        self.assertEqual(StringUtils.prepare_escape_chars("abc\\rdef"), "abc\rdef")
        self.assertEqual(StringUtils.prepare_escape_chars("abc\\\\def"), "abc\\def")
        self.assertEqual(StringUtils.prepare_escape_chars("abc\\\"def"), "abc\"def")
        self.assertEqual(StringUtils.prepare_escape_chars("abc\\'def"), "abc'def")
        
        self.assertEqual(StringUtils.prepare_escape_chars(""), "")
        self.assertEqual(StringUtils.prepare_escape_chars(None), "")
    
    def test_split_with_quotes(self):
        """Test split_with_quotes method."""
        self.assertEqual(
            StringUtils.split_with_quotes("a,b,c"),
            ["a", "b", "c"]
        )
        
        self.assertEqual(
            StringUtils.split_with_quotes("a,\"b,c\",d"),
            ["a", "\"b,c\"", "d"]
        )
        
        self.assertEqual(
            StringUtils.split_with_quotes("\"a,b\",c,\"d,e,f\""),
            ["\"a,b\"", "c", "\"d,e,f\""]
        )
        
        self.assertEqual(StringUtils.split_with_quotes(""), [])
        self.assertEqual(StringUtils.split_with_quotes("a"), ["a"])
    
    def test_parse_key_value_pairs(self):
        """Test parse_key_value_pairs method."""
        self.assertEqual(
            StringUtils.parse_key_value_pairs("a=1,b=2,c=3"),
            {"a": "1", "b": "2", "c": "3"}
        )
        
        self.assertEqual(
            StringUtils.parse_key_value_pairs("a=1, b=2, c=3"),
            {"a": "1", "b": "2", "c": "3"}
        )
        
        self.assertEqual(
            StringUtils.parse_key_value_pairs("a=\"1,2\",b=3"),
            {"a": "\"1,2\"", "b": "3"}
        )
        
        self.assertEqual(StringUtils.parse_key_value_pairs(""), {})
        self.assertEqual(StringUtils.parse_key_value_pairs("a"), {})
        self.assertEqual(StringUtils.parse_key_value_pairs("a,b,c"), {})


class TestTextFormat(unittest.TestCase):
    """Tests for the TextFormat enum."""
    
    def test_enum_values(self):
        """Test enum values."""
        self.assertEqual(TextFormat.FIXED_LENGTH.value, "FL")
        self.assertEqual(TextFormat.DELIMITED.value, "DEL")
        self.assertEqual(TextFormat.UNKNOWN.value, "UNKNOWN")


class TestExceptions(unittest.TestCase):
    """Tests for the exception classes."""
    
    def test_flat_file_error(self):
        """Test FlatFileError."""
        error = FlatFileError("Test error")
        self.assertEqual(str(error), "Test error")
    
    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Test validation error")
        self.assertEqual(str(error), "Test validation error")
        self.assertIsInstance(error, FlatFileError)
    
    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Test configuration error")
        self.assertEqual(str(error), "Test configuration error")
        self.assertIsInstance(error, FlatFileError)


if __name__ == '__main__':
    unittest.main() 