"""
Validator classes for FlatForge.
"""
from abc import ABC, abstractmethod
from datetime import datetime
import re
from decimal import Decimal
from typing import Dict, List, Optional, Any, Set, Protocol, NamedTuple
from collections import defaultdict
import logging

from .models import Rule, GlobalRule, FileProperties, RuleResult, Message, CellId, MessageSeverity
from .utils import TextFormat, is_blank, is_not_blank, get_digits, contains_trimmed, contains_ignore_case_list, left_pad, StringUtils

# Set up logging
logger = logging.getLogger(__name__)


class ValidationContext(NamedTuple):
    """Context for validation operations."""
    column_index: int
    section_index: str
    record_index: int
    record_number_within_section: int
    record: str
    columns: List[str]
    file_props: FileProperties


class Validator(Protocol):
    """Protocol for validators."""
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Validate a value against a rule."""
        pass


class ValidatorAdapter:
    """Base adapter for validators."""
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Validate a field value."""
        return RuleResult()
    
    def trim_parameters(self, rule: Rule) -> None:
        """Trim parameters in a rule."""
        if rule.parameters:
            rule.parameters = [p.strip() if p else p for p in rule.parameters]


class NumberValidator(ValidatorAdapter):
    """Validator for numeric fields."""
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Validate a numeric field."""
        result = RuleResult()
        self.trim_parameters(rule)
        
        max_size = -1
        decimals = -1
        min_size = -1
        min_decimals = False
        
        # Parse parameters
        if not rule.parameters:
            max_size = -1
        else:
            if len(rule.parameters) >= 1 and is_not_blank(rule.parameters[0]):
                max_size = int(rule.parameters[0])
            
            if len(rule.parameters) >= 2 and is_not_blank(rule.parameters[1]):
                if 'm' in rule.parameters[1]:
                    min_decimals = True
                
                decimals = int(get_digits(rule.parameters[1])[0])
            
            if len(rule.parameters) >= 3 and is_not_blank(rule.parameters[2]):
                min_size = int(rule.parameters[2])
        
        # Validate decimals
        if decimals > 0:
            if '.' not in value:
                result.add_message(Message(
                    text="Missing decimal point",
                    code="0003",
                    section_index=context.section_index,
                    column_index=context.column_index,
                    severity=MessageSeverity.ERROR.value,
                    value=context.columns[context.column_index],
                    is_error=True,
                    column_alias=context.file_props.get_column_alias(context.section_index, context.column_index)
                ))
            elif value.count('.') > 1:
                result.add_message(Message(
                    text="Too many decimal points",
                    code="0005",
                    section_index=context.section_index,
                    column_index=context.column_index,
                    severity=MessageSeverity.ERROR.value,
                    value=context.columns[context.column_index],
                    is_error=True,
                    column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                    parameters={"{0}": value}
                ))
            else:
                decimals_count = len(value) - value.index('.') - 1
                
                if min_decimals:
                    if decimals_count < decimals:
                        result.add_message(Message(
                            text="Incorrect number of decimal places",
                            code="0004",
                            section_index=context.section_index,
                            column_index=context.column_index,
                            severity=MessageSeverity.ERROR.value,
                            value=context.columns[context.column_index],
                            is_error=True,
                            column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                            parameters={"{0}": str(decimals_count), "{1}": str(decimals)}
                        ))
                elif decimals_count != decimals:
                    result.add_message(Message(
                        text="Incorrect number of decimal places",
                        code="0004",
                        section_index=context.section_index,
                        column_index=context.column_index,
                        severity=MessageSeverity.ERROR.value,
                        value=context.columns[context.column_index],
                        is_error=True,
                        column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                        parameters={"{0}": str(decimals_count), "{1}": str(decimals)}
                    ))
        elif decimals == 0 and '.' in value:
            result.add_message(Message(
                text="Decimal point not allowed",
                code="0006",
                section_index=context.section_index,
                column_index=context.column_index,
                severity=MessageSeverity.ERROR.value,
                value=context.columns[context.column_index],
                is_error=True,
                column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                parameters={"{0}": value}
            ))
        
        # Validate numeric value
        try:
            if context.file_props.allow_space_to_pad_numbers:
                value = value.strip()
            
            num_value = float(value)
            
            # Validate size
            if max_size > 0:
                int_part = value.split('.')[0]
                if len(int_part) > max_size:
                    result.add_message(Message(
                        text="Integer part too long",
                        code="0007",
                        section_index=context.section_index,
                        column_index=context.column_index,
                        severity=MessageSeverity.ERROR.value,
                        value=context.columns[context.column_index],
                        is_error=True,
                        column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                        parameters={"{0}": str(len(int_part)), "{1}": str(max_size)}
                    ))
            
            # Validate minimum size
            if min_size > 0:
                if num_value < min_size:
                    result.add_message(Message(
                        text="Value too small",
                        code="0008",
                        section_index=context.section_index,
                        column_index=context.column_index,
                        severity=MessageSeverity.ERROR.value,
                        value=context.columns[context.column_index],
                        is_error=True,
                        column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                        parameters={"{0}": str(num_value), "{1}": str(min_size)}
                    ))
        except ValueError:
            result.add_message(Message(
                text="Invalid numeric value",
                code="0002",
                section_index=context.section_index,
                column_index=context.column_index,
                severity=MessageSeverity.ERROR.value,
                value=context.columns[context.column_index],
                is_error=True,
                column_alias=context.file_props.get_column_alias(context.section_index, context.column_index)
            ))
        
        return result


class StringValidator(ValidatorAdapter):
    """Validator for string fields."""
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Validate a string field."""
        result = RuleResult()
        self.trim_parameters(rule)
        
        # Handle different rule types
        if rule.name == "required":
            if not value:
                result.add_message(Message(
                    text="Required field is empty",
                    code="0100",
                    section_index=context.section_index,
                    column_index=context.column_index,
                    severity=MessageSeverity.ERROR.value,
                    value=context.columns[context.column_index],
                    is_error=True,
                    column_alias=context.file_props.get_column_alias(context.section_index, context.column_index)
                ))
        elif rule.name == "length":
            # Parse parameters
            min_length = -1
            max_length = -1
            
            if rule.parameters:
                if len(rule.parameters) >= 1 and is_not_blank(rule.parameters[0]):
                    max_length = int(rule.parameters[0])
                
                if len(rule.parameters) >= 2 and is_not_blank(rule.parameters[1]):
                    min_length = int(rule.parameters[1])
            
            # Validate length
            if max_length > 0 and len(value) > max_length:
                result.add_message(Message(
                    text="String too long",
                    code="0101",
                    section_index=context.section_index,
                    column_index=context.column_index,
                    severity=MessageSeverity.ERROR.value,
                    value=context.columns[context.column_index],
                    is_error=True,
                    column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                    parameters={"{0}": str(len(value)), "{1}": str(max_length)}
                ))
            
            if min_length > 0 and len(value) < min_length:
                result.add_message(Message(
                    text="String too short",
                    code="0102",
                    section_index=context.section_index,
                    column_index=context.column_index,
                    severity=MessageSeverity.ERROR.value,
                    value=context.columns[context.column_index],
                    is_error=True,
                    column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                    parameters={"{0}": str(len(value)), "{1}": str(min_length)}
                ))
        elif rule.name == "regex":
            # Check if the value matches the regex pattern
            if rule.parameters and len(rule.parameters) > 0:
                pattern = rule.parameters[0]
                if not StringUtils.matches_regex(value, pattern):
                    result.add_message(Message(
                        text="String does not match pattern",
                        code="0103",
                        section_index=context.section_index,
                        column_index=context.column_index,
                        severity=MessageSeverity.ERROR.value,
                        value=context.columns[context.column_index],
                        is_error=True,
                        column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                        parameters={"{0}": value, "{1}": pattern}
                    ))
        
        return result


class ChoiceValidator(ValidatorAdapter):
    """Validator for choice fields."""
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Validate a choice field."""
        result = RuleResult()
        self.trim_parameters(rule)
        
        if not rule.parameters:
            return result
        
        # Check if value is in the list of valid choices
        valid_choices = rule.parameters
        
        if value not in valid_choices:
            # For fixed-length format, check with trimming
            if context.file_props.get_text_format_for_section(context.section_index) == TextFormat.FIXED_LENGTH.value:
                found = False
                for choice in valid_choices:
                    if contains_trimmed(value, choice):
                        found = True
                        break
                
                if not found:
                    result.add_message(Message(
                        text="Invalid choice",
                        code="0201",
                        section_index=context.section_index,
                        column_index=context.column_index,
                        severity=MessageSeverity.ERROR.value,
                        value=context.columns[context.column_index],
                        is_error=True,
                        column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                        parameters={"{0}": value, "{1}": ", ".join(valid_choices)}
                    ))
            else:
                result.add_message(Message(
                    text="Invalid choice",
                    code="0201",
                    section_index=context.section_index,
                    column_index=context.column_index,
                    severity=MessageSeverity.ERROR.value,
                    value=context.columns[context.column_index],
                    is_error=True,
                    column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                    parameters={"{0}": value, "{1}": ", ".join(valid_choices)}
                ))
        
        return result


class IChoiceValidator(ValidatorAdapter):
    """Validator for case-insensitive choice fields."""
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Validate a case-insensitive choice field."""
        result = RuleResult()
        self.trim_parameters(rule)
        
        if not rule.parameters:
            return result
        
        # Check if value is in the list of valid choices (case-insensitive)
        valid_choices = rule.parameters
        
        # For fixed-length format, trim the value
        if context.file_props.get_text_format_for_section(context.section_index) == TextFormat.FIXED_LENGTH.value:
            value = value.strip()
        
        # Check if value is in the list (case-insensitive)
        if not contains_ignore_case_list(value, valid_choices):
            result.add_message(Message(
                code="0201",
                section_index=context.section_index,
                column_index=context.column_index,
                severity=MessageSeverity.ERROR.value,
                value=context.columns[context.column_index],
                is_error=True,
                column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                parameters={"{0}": value, "{1}": ", ".join(valid_choices)}
            ))
        
        return result


class PrefixValidator(ValidatorAdapter):
    """Validator for prefix fields."""
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Validate that a field starts with a specific prefix."""
        result = RuleResult()
        self.trim_parameters(rule)
        
        if not rule.parameters:
            return result
        
        prefix = rule.parameters[0]
        
        # Create parameters for error message
        parameters = {"{0}": value, "{1}": prefix}
        
        # Check if value starts with prefix
        if not value.startswith(prefix):
            # For fixed-length format, check with trimming
            if context.file_props.get_text_format_for_section(context.section_index) == TextFormat.FIXED_LENGTH.value:
                if not value.strip().startswith(prefix):
                    result.add_message(Message(
                        text="Value does not start with required prefix",
                        code="0401",
                        section_index=context.section_index,
                        column_index=context.column_index,
                        severity=MessageSeverity.ERROR.value,
                        value=context.columns[context.column_index],
                        is_error=True,
                        column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                        parameters=parameters
                    ))
            else:
                result.add_message(Message(
                    text="Value does not start with required prefix",
                    code="0402",
                    section_index=context.section_index,
                    column_index=context.column_index,
                    severity=MessageSeverity.ERROR.value,
                    value=context.columns[context.column_index],
                    is_error=True,
                    column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                    parameters=parameters
                ))
        
        return result


class SuffixValidator(ValidatorAdapter):
    """Validator for suffix fields."""
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Validate that a field ends with a specific suffix."""
        result = RuleResult()
        self.trim_parameters(rule)
        
        if not rule.parameters:
            return result
        
        suffix = rule.parameters[0]
        
        # Create parameters for error message
        parameters = {"{0}": value, "{1}": suffix}
        
        # Check if value ends with suffix
        if not value.endswith(suffix):
            # For fixed-length format, check with trimming
            if context.file_props.get_text_format_for_section(context.section_index) == TextFormat.FIXED_LENGTH.value:
                if not value.strip().endswith(suffix):
                    result.add_message(Message(
                        text="Value does not end with required suffix",
                        code="0403",
                        section_index=context.section_index,
                        column_index=context.column_index,
                        severity=MessageSeverity.ERROR.value,
                        value=context.columns[context.column_index],
                        is_error=True,
                        column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                        parameters=parameters
                    ))
            else:
                result.add_message(Message(
                    text="Value does not end with required suffix",
                    code="0404",
                    section_index=context.section_index,
                    column_index=context.column_index,
                    severity=MessageSeverity.ERROR.value,
                    value=context.columns[context.column_index],
                    is_error=True,
                    column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                    parameters=parameters
                ))
        
        return result


class PutValidator(ValidatorAdapter):
    """Validator for put fields."""
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Replace the field value with a specified value."""
        result = RuleResult()
        self.trim_parameters(rule)
        
        if not rule.parameters:
            raise ValueError("put rule must have parameters!")
        
        # Simple replacement with a single parameter
        if len(rule.parameters) == 1 and "?" not in rule.parameters[0]:
            context.columns[context.column_index] = rule.parameters[0]
        else:
            # Conditional replacement based on value matching
            for param in rule.parameters:
                if param:
                    parts = param.split("?", 1)
                    if len(parts) != 2:
                        raise ValueError("put rule must have 2 sides of a condition!")
                    
                    if value == parts[0]:
                        context.columns[context.column_index] = parts[1]
                        break
        
        return result


class TrimValidator(ValidatorAdapter):
    """Validator for trim fields."""
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Trim whitespace from the field value."""
        result = RuleResult()
        
        # Trim the value and update the column
        context.columns[context.column_index] = value.strip()
        
        return result


class UniqueValidator(ValidatorAdapter):
    """Validator for unique fields."""
    
    def __init__(self):
        """Initialize the validator."""
        super().__init__()
        self.unique_values = defaultdict(set)
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Validate that a field value is unique."""
        result = RuleResult()
        
        if value is None:
            result.add_message(Message(
                text="Value is null",
                code="0501",
                section_index=context.section_index,
                column_index=context.column_index,
                severity=MessageSeverity.ERROR.value,
                value=context.columns[context.column_index],
                is_error=True,
                column_alias=context.file_props.get_column_alias(context.section_index, context.column_index)
            ))
            return result
        
        if rule.is_optional:
            raise ValueError("Unique constraint cannot be optional!")
        
        # Create a unique key for this column
        column_key = f"{context.section_index}:{context.column_index}"
        
        # Check if value is already in the set
        if value in self.unique_values[column_key]:
            result.add_message(Message(
                text="Duplicate value",
                code="0502",
                section_index=context.section_index,
                column_index=context.column_index,
                severity=MessageSeverity.ERROR.value,
                value=context.columns[context.column_index],
                is_error=True,
                column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                parameters={"{0}": value}
            ))
        else:
            # Add value to the set
            self.unique_values[column_key].add(value)
        
        return result


class DateValidator(ValidatorAdapter):
    """Validator for date fields."""
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Validate a date field."""
        result = RuleResult()
        self.trim_parameters(rule)
        
        if not rule.parameters or not rule.parameters[0]:
            return result
        
        date_format = rule.parameters[0]
        
        try:
            # Try to parse the date with the specified format
            datetime.strptime(value, date_format)
        except ValueError:
            result.add_message(Message(
                text="Invalid date format",
                code="0301",
                section_index=context.section_index,
                column_index=context.column_index,
                severity=MessageSeverity.ERROR.value,
                value=context.columns[context.column_index],
                is_error=True,
                column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                parameters={"{0}": value, "{1}": date_format}
            ))
        
        return result


class CrossRecordValidatorAdapter(ValidatorAdapter):
    """Base adapter for cross-record validators."""
    
    def __init__(self):
        self.crc_watchlist = {}


class SumCrValidator(CrossRecordValidatorAdapter):
    """Validator for sum cross-record checks."""
    
    def update_crc_watchlist(self, cr_check: GlobalRule, section_index: str, file_props: FileProperties, columns: List[str]):
        """Update the cross-record check watchlist."""
        if section_index == cr_check.section_index:
            cell_id = CellId(cr_check.section_index, cr_check.column_to_watch)
            key = (cell_id.__str__(), "sum")
            
            value = self.crc_watchlist.get(key, Decimal('0'))
            
            str_value = columns[cr_check.column_to_watch]
            if file_props.allow_space_to_pad_numbers:
                str_value = str_value.strip()
            
            value += Decimal(str_value)
            self.crc_watchlist[key] = value
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Validate a sum cross-record check."""
        result = RuleResult()
        self.trim_parameters(rule)
        
        if isinstance(rule, GlobalRule):
            cr_check = rule
            cell_id = CellId(cr_check.section_index, cr_check.column_to_watch)
            
            if cr_check.read_start_index != -1 and cr_check.read_end_index != -1:
                try:
                    str_value = context.columns[cr_check.column_to_watch][cr_check.read_start_index:cr_check.read_end_index]
                except Exception:
                    str_value = None
                
                key = (f"{cell_id.__str__()}{':' + str_value if str_value else ''}", "sum")
                bd_value = self.crc_watchlist.get(key, Decimal('1'))
                bd_value += Decimal('1')
                self.crc_watchlist[key] = bd_value
            else:
                key = (cell_id.__str__(), "sum")
            
            total = self.crc_watchlist.get(key, Decimal('0'))
            
            if cr_check.write_start_index != -1 and cr_check.write_end_index != -1:
                try:
                    bd_value = Decimal(value[cr_check.write_start_index:cr_check.write_end_index].strip())
                except Exception:
                    bd_value = Decimal('-1')
            else:
                bd_value = Decimal(value.strip())
            
            if cr_check.action == "match":
                if total != bd_value:
                    result.add_message(Message(
                        text="Sum does not match expected value",
                        code="0500",
                        section_index=context.section_index,
                        column_index=context.column_index,
                        severity=MessageSeverity.ERROR.value,
                        value=context.columns[context.column_index],
                        is_error=True,
                        column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                        parameters={"{0}": str(total)}
                    ))
            elif cr_check.action == "put":
                if cr_check.write_start_index != -1 and cr_check.write_end_index != -1:
                    context.columns[context.column_index] = (
                        context.columns[context.column_index][:cr_check.write_start_index] +
                        left_pad(str(total), cr_check.write_end_index - cr_check.write_start_index) +
                        context.columns[context.column_index][cr_check.write_end_index:]
                    )
                else:
                    context.columns[context.column_index] = str(total)
        
        return result


class CountCrValidator(CrossRecordValidatorAdapter):
    """Validator for count cross-record checks."""
    
    def update_crc_watchlist(self, cr_check: GlobalRule, section_index: str, file_props: FileProperties, columns: List[str]):
        """Update the cross-record check watchlist."""
        if section_index == cr_check.section_index:
            cell_id = CellId(cr_check.section_index, cr_check.column_to_watch)
            key = (cell_id.__str__(), "count")
            
            value = self.crc_watchlist.get(key, 0)
            value += 1
            self.crc_watchlist[key] = value
    
    def validate(self, rule: Rule, value: str, context: ValidationContext) -> RuleResult:
        """Validate a count cross-record check."""
        result = RuleResult()
        self.trim_parameters(rule)
        
        if isinstance(rule, GlobalRule):
            cr_check = rule
            cell_id = CellId(cr_check.section_index, cr_check.column_to_watch)
            
            if cr_check.read_start_index != -1 and cr_check.read_end_index != -1:
                try:
                    str_value = context.columns[cr_check.column_to_watch][cr_check.read_start_index:cr_check.read_end_index]
                except Exception:
                    str_value = None
                
                key = (f"{cell_id.__str__()}{':' + str_value if str_value else ''}", "count")
                count_value = self.crc_watchlist.get(key, 0)
                count_value += 1
                self.crc_watchlist[key] = count_value
            else:
                key = (cell_id.__str__(), "count")
            
            total = self.crc_watchlist.get(key, 0)
            
            if cr_check.write_start_index != -1 and cr_check.write_end_index != -1:
                try:
                    count_value = int(value[cr_check.write_start_index:cr_check.write_end_index].strip())
                except Exception:
                    count_value = -1
            else:
                count_value = int(value.strip())
            
            if cr_check.action == "match":
                if total != count_value:
                    result.add_message(Message(
                        text="Count does not match expected value",
                        code="0501",
                        section_index=context.section_index,
                        column_index=context.column_index,
                        severity=MessageSeverity.ERROR.value,
                        value=context.columns[context.column_index],
                        is_error=True,
                        column_alias=context.file_props.get_column_alias(context.section_index, context.column_index),
                        parameters={"{0}": str(total)}
                    ))
            elif cr_check.action == "put":
                if cr_check.write_start_index != -1 and cr_check.write_end_index != -1:
                    context.columns[context.column_index] = (
                        context.columns[context.column_index][:cr_check.write_start_index] +
                        left_pad(str(total), cr_check.write_end_index - cr_check.write_start_index) +
                        context.columns[context.column_index][cr_check.write_end_index:]
                    )
                else:
                    context.columns[context.column_index] = str(total)
        
        return result 