"""
Utility functions and classes for FlatForge.
"""
import re
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Pattern, Tuple
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)


class TextFormat(Enum):
    """Enumeration of supported text formats."""
    FIXED_LENGTH = "FL"
    DELIMITED = "DEL"
    UNKNOWN = "UNKNOWN"


class FlatFileError(Exception):
    """Base exception for all FlatForge errors."""
    pass


class ValidationError(FlatFileError):
    """Exception raised for validation errors."""
    pass


class ConfigurationError(FlatFileError):
    """Exception raised for configuration errors."""
    pass


class ParserError(FlatFileError):
    """Exception raised for parsing errors."""
    
    def __init__(self, error_code, values=None):
        self.error_code = error_code
        self.values = values or {}
        super().__init__(f"Parser error: {error_code}")


class StringUtils:
    """Utility methods for string operations."""
    
    @staticmethod
    def is_empty(value: str) -> bool:
        """Check if a string is empty or None."""
        return value is None or value.strip() == ""
    
    @staticmethod
    def is_blank(value: str) -> bool:
        """Check if a string is blank or None."""
        return value is None or value.strip() == ""
    
    @staticmethod
    def matches_regex(value: str, pattern: str) -> bool:
        """Check if a string matches a regular expression pattern."""
        try:
            return bool(re.match(pattern, value))
        except re.error:
            logger.error(f"Invalid regex pattern: {pattern}")
            return False
    
    @staticmethod
    def is_numeric(value: str) -> bool:
        """Check if a string is numeric."""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_date(value: str, date_format: str) -> bool:
        """Check if a string is a valid date in the specified format."""
        try:
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def split(text: str, delimiter: str, trim: bool = False) -> List[str]:
        """Split a string by a delimiter."""
        if text is None:
            return []
        
        if text == "":
            return []
        
        parts = text.split(delimiter)
        
        if trim:
            parts = [part.strip() for part in parts]
        
        return parts
    
    @staticmethod
    def split_with_qualifier(text: str, delimiter: str, trim: bool = False, qualifier: str = '"') -> List[str]:
        """Split a string by a delimiter, respecting qualifiers."""
        if text is None:
            return []
        
        if text == "":
            return []
        
        # Simple case: no qualifier
        if qualifier is None or qualifier == "":
            return StringUtils.split(text, delimiter, trim)
        
        # Complex case: with qualifier
        parts = []
        current_part = ""
        in_quotes = False
        
        for char in text:
            if char == qualifier:
                in_quotes = not in_quotes
                current_part += char
            elif char == delimiter and not in_quotes:
                parts.append(current_part)
                current_part = ""
            else:
                current_part += char
        
        parts.append(current_part)
        
        if trim:
            parts = [part.strip() for part in parts]
        
        return parts
    
    @staticmethod
    def prepare_escape_chars(value: str) -> str:
        """Process escape characters in a string."""
        if value is None:
            return ""
        
        # Replace escape sequences
        value = value.replace("\\n", "\n")
        value = value.replace("\\r", "\r")
        value = value.replace("\\t", "\t")
        value = value.replace("\\\"", "\"")
        value = value.replace("\\'", "'")
        value = value.replace("\\\\", "\\")
        
        return value
    
    @staticmethod
    def split_with_quotes(text: str, delimiter: str = ',', quote_char: str = '"') -> List[str]:
        """
        Split a string by a delimiter, respecting quoted sections.
        
        Args:
            text: The string to split
            delimiter: The delimiter character
            quote_char: The quote character
            
        Returns:
            List of split strings
        """
        if not text:
            return []
        
        result = []
        current = []
        in_quotes = False
        
        for char in text:
            if char == quote_char:
                in_quotes = not in_quotes
                current.append(char)
            elif char == delimiter and not in_quotes:
                result.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
        
        if current:
            result.append(''.join(current).strip())
        
        return result
    
    @staticmethod
    def parse_key_value_pairs(text: str, item_delimiter: str = ',', kv_delimiter: str = '=') -> Dict[str, str]:
        """
        Parse a string of key-value pairs into a dictionary.
        
        Args:
            text: The string to parse (e.g., "key1=value1,key2=value2")
            item_delimiter: The delimiter between items
            kv_delimiter: The delimiter between keys and values
            
        Returns:
            Dictionary of key-value pairs
        """
        if not text:
            return {}
        
        result = {}
        items = StringUtils.split_with_quotes(text, item_delimiter)
        
        for item in items:
            if kv_delimiter in item:
                key, value = item.split(kv_delimiter, 1)
                result[key.strip()] = value.strip()
        
        return result


def split_string(text: str, delimiter: str, trim: bool = False) -> List[str]:
    """Split a string by a delimiter."""
    return StringUtils.split(text, delimiter, trim)


def split_with_qualifier(text: str, delimiter: str, trim: bool = False, qualifier: str = None) -> List[str]:
    """Split a string by a delimiter, respecting qualifiers."""
    return StringUtils.split_with_qualifier(text, delimiter, trim, qualifier)


def is_blank(text: str) -> bool:
    """Check if a string is blank."""
    return text is None or text.strip() == ""


def is_not_blank(text: str) -> bool:
    """Check if a string is not blank."""
    return not is_blank(text)


def get_digits(text: str) -> List[str]:
    """Extract digits from a string."""
    if not text:
        return []
    
    result = []
    current = ""
    
    for char in text:
        if char.isdigit():
            current += char
        elif current:
            result.append(current)
            current = ""
    
    if current:
        result.append(current)
    
    return result


def left_pad(text: str, length: int, pad_char: str = ' ') -> str:
    """Pad a string on the left."""
    return text.rjust(length, pad_char)


def right_pad(text: str, length: int, pad_char: str = ' ') -> str:
    """Pad a string on the right."""
    return text.ljust(length, pad_char)


def contains_trimmed(text: str, substring: str) -> bool:
    """Check if a string contains a substring after trimming."""
    return substring.strip() in text.strip()


def contains_ignore_case(text: str, substring: str) -> bool:
    """Check if a string contains a substring, ignoring case."""
    return substring.lower() in text.lower()


def contains_ignore_case_list(text: str, substrings: List[str]) -> bool:
    """Check if a string contains any substring from a list, ignoring case."""
    text_lower = text.lower()
    return any(substring.lower() in text_lower for substring in substrings)


def get_int(value: str) -> int:
    """Convert a string to an integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return -1


def ensure_directory_exists(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)


class ConfigParserUtil:
    """Utility methods for configuration parsing."""
    
    @staticmethod
    def convert_to_maps(text: str) -> Tuple[Dict[str, str], Dict[str, Dict[str, str]]]:
        """Convert a configuration text to maps."""
        config = {}
        arrays = {}
        
        # Split the text into lines
        lines = text.splitlines()
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Check if this is a section header
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].strip()
                arrays[current_section] = {}
                continue
            
            # Skip lines without a current section
            if current_section is None:
                continue
            
            # Parse key-value pairs
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                if current_section == "parameters":
                    config[key] = value
                else:
                    arrays[current_section][key] = value
        
        return config, arrays
    
    @staticmethod
    def prepare_escape_chars(value: str) -> str:
        """Process escape characters in a string."""
        if value is None:
            return ""
        
        # Replace escape sequences
        value = value.replace("\\n", "\n")
        value = value.replace("\\r", "\r")
        value = value.replace("\\t", "\t")
        value = value.replace("\\\"", "\"")
        value = value.replace("\\'", "'")
        value = value.replace("\\\\", "\\")
        
        return value 