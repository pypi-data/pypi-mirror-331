"""Tests for the validators module."""
import unittest
from unittest.mock import patch, MagicMock

from flatforge.validators import ValidationContext
from flatforge.validators import NumberValidator, StringValidator, ChoiceValidator, DateValidator
from flatforge.models import Rule, FileProperties, RuleResult, Message, MessageSeverity
from flatforge.validators import ValidatorAdapter


def create_mock_file_props():
    """Create a mock FileProperties instance."""
    ffmd = MagicMock(spec=FileProperties)
    ffmd.get_parameter.return_value = None
    return ffmd


class TestValidator(unittest.TestCase):
    """Tests for the Validator class."""
    
    def test_init(self):
        """Test initialization of Validator."""
        validator = ValidatorAdapter()
        self.assertIsInstance(validator, ValidatorAdapter)
    
    def test_validate(self):
        """Test validate method."""
        validator = ValidatorAdapter()
        context = ValidationContext(
            column_index=0,
            section_index="0",
            record_index=0,
            record_number_within_section=0,
            record="test",
            columns=["test"],
            file_props=create_mock_file_props()
        )
        result = validator.validate(Rule(name="test"), "test", context)
        self.assertIsInstance(result, RuleResult)


class TestNumberValidator(unittest.TestCase):
    """Tests for the NumberValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = NumberValidator()
        self.context = ValidationContext(
            column_index=0,
            section_index="0",
            record_index=0,
            record_number_within_section=0,
            record="123",
            columns=["123"],
            file_props=create_mock_file_props()
        )
    
    def test_validate_valid_number(self):
        """Test validating a valid number."""
        rule = Rule(name="numeric")
        result = self.validator.validate(rule, "123", self.context)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.message)
        
        result = self.validator.validate(rule, "123.45", self.context)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.message)
        
        result = self.validator.validate(rule, "-123", self.context)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.message)
    
    def test_validate_invalid_number(self):
        """Test validating an invalid number."""
        rule = Rule(name="numeric")
        result = self.validator.validate(rule, "abc", self.context)
        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.message)
        self.assertTrue(result.message.is_error)
        
        result = self.validator.validate(rule, "123abc", self.context)
        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.message)
        
        result = self.validator.validate(rule, "", self.context)
        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.message)


class TestStringValidator(unittest.TestCase):
    """Tests for the StringValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = StringValidator()
        self.context = ValidationContext(
            column_index=0,
            section_index="0",
            record_index=0,
            record_number_within_section=0,
            record="test",
            columns=["test"],
            file_props=create_mock_file_props()
        )
    
    def test_validate_required(self):
        """Test validating a required string."""
        # Set up rule for required validation
        rule = Rule(name="required")
        
        # Test with non-empty string
        result = self.validator.validate(rule, "test", self.context)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.message)
        
        # Test with empty string
        result = self.validator.validate(rule, "", self.context)
        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.message)
        self.assertTrue(result.message.is_error)
    
    def test_validate_length(self):
        """Test validating string length."""
        # Set up rule for length validation
        rule = Rule(name="length", parameters=["5"])
        
        # Test with string of correct length
        result = self.validator.validate(rule, "12345", self.context)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.message)
        
        # Test with string that's too long
        result = self.validator.validate(rule, "123456", self.context)
        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.message)
        self.assertTrue(result.message.is_error)
    
    def test_validate_regex(self):
        """Test validating string against regex."""
        # Set up rule for regex validation
        rule = Rule(name="regex", parameters=["[A-Z]{3}"])
        
        # Test with string that matches regex
        result = self.validator.validate(rule, "ABC", self.context)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.message)
        
        # Test with string that doesn't match regex
        result = self.validator.validate(rule, "abc", self.context)
        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.message)
        self.assertTrue(result.message.is_error)


class TestChoiceValidator(unittest.TestCase):
    """Tests for the ChoiceValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = ChoiceValidator()
        self.context = ValidationContext(
            column_index=0,
            section_index="0",
            record_index=0,
            record_number_within_section=0,
            record="A",
            columns=["A"],
            file_props=create_mock_file_props()
        )
    
    def test_validate_valid_choice(self):
        """Test validating a valid choice."""
        rule = Rule(name="choice", parameters=["A", "B", "C"])
        result = self.validator.validate(rule, "A", self.context)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.message)
        
        result = self.validator.validate(rule, "B", self.context)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.message)
        
        result = self.validator.validate(rule, "C", self.context)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.message)
    
    def test_validate_invalid_choice(self):
        """Test validating an invalid choice."""
        rule = Rule(name="choice", parameters=["A", "B", "C"])
        result = self.validator.validate(rule, "D", self.context)
        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.message)
        self.assertTrue(result.message.is_error)
        
        result = self.validator.validate(rule, "", self.context)
        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.message)


class TestDateValidator(unittest.TestCase):
    """Tests for the DateValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = DateValidator()
        self.context = ValidationContext(
            column_index=0,
            section_index="0",
            record_index=0,
            record_number_within_section=0,
            record="2021-01-01",
            columns=["2021-01-01"],
            file_props=create_mock_file_props()
        )
    
    def test_validate_valid_date(self):
        """Test validating a valid date."""
        rule = Rule(name="date", parameters=["%Y-%m-%d"])
        result = self.validator.validate(rule, "2023-01-01", self.context)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.message)
        
        result = self.validator.validate(rule, "2023-12-31", self.context)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.message)
    
    def test_validate_invalid_date(self):
        """Test validating an invalid date."""
        rule = Rule(name="date", parameters=["%Y-%m-%d"])
        result = self.validator.validate(rule, "2023-13-01", self.context)
        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.message)
        self.assertTrue(result.message.is_error)
        
        result = self.validator.validate(rule, "invalid-date", self.context)
        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.message)
        
        result = self.validator.validate(rule, "", self.context)
        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.message)


if __name__ == "__main__":
    unittest.main() 