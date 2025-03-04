"""
Core data models for the FlatForge.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from .utils import TextFormat


@dataclass
class Rule:
    """Represents a validation rule for a field."""
    name: str
    parameters: Optional[List[str]] = None
    column_alias: Optional[str] = None
    is_optional: bool = False

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []


@dataclass
class GlobalRule(Rule):
    """Represents a global validation rule that works across records."""
    section_index: str = "-1"
    column_index: int = -1
    read_start_index: int = -1
    read_end_index: int = -1
    write_start_index: int = -1
    write_end_index: int = -1
    action: Optional[str] = None

    def __str__(self) -> str:
        params_str = f"({','.join(self.parameters)})" if self.parameters else ""
        alias_str = f", alias={self.column_alias}" if self.column_alias else ""
        optional_str = ", optional=True" if self.is_optional else ""
        return f"{self.name}{params_str} [section_index={self.section_index}, column_index={self.column_index}{alias_str}{optional_str}]"


@dataclass
class Section:
    """Represents a section in a flat file."""
    index: str
    section_format: Optional[str] = None
    length: int = 0
    rules: Dict[int, List[Rule]] = field(default_factory=dict)
    instructions: List[Rule] = field(default_factory=list)
    valid_column_counts: Optional[List[int]] = None

    def __str__(self) -> str:
        """String representation of the section."""
        return f"Section {self.index} (format={self.section_format}, length={self.length})"

    def get_instruction(self, rule_name: str) -> Optional[Rule]:
        """Get an instruction by name."""
        if self.instructions:
            for instruction in self.instructions:
                if instruction.name == rule_name:
                    return instruction
        return None

    def get_rules(self, column_index: int) -> List[Rule]:
        """Get rules for a specific column."""
        return self.rules.get(column_index, [])

    def get_columns_count(self) -> int:
        """Get the number of columns in this section."""
        return len(self.rules) if self.rules else 0

    def is_valid_column_count(self, column_count: int) -> bool:
        """Check if the column count is valid for this section."""
        if self.valid_column_counts:
            return column_count in self.valid_column_counts
        return True


class MessageSeverity(Enum):
    """Severity levels for messages."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class FileProperties:
    """Properties for a flat file."""
    # Properties
    encoding: str = "UTF-8"
    text_format_code: Optional[str] = None
    section_separator: Optional[str] = None
    record_separator: str = "\n"
    field_separator: Optional[str] = None
    other_separator: Optional[str] = None
    text_qualifier: Optional[str] = None
    section_identity_column_index: int = -1
    ignore_blank_rows: bool = False
    accept_trailing_white_space: bool = False
    allow_space_to_pad_numbers: bool = False
    error_separator: Optional[str] = None
    error_format: Optional[str] = None
    
    sections: Dict[str, Section] = field(default_factory=dict)
    global_rules: List[GlobalRule] = field(default_factory=list)
    parameters: Dict[str, str] = field(default_factory=dict)
    arrays: Dict[str, Dict] = field(default_factory=dict)

    def set_parameters(self, parameters: Dict[str, str]):
        """Set parameters from a dictionary."""
        self.parameters = parameters
        
        # Set properties from parameters
        self.text_format_code = parameters.get("text_format_code")
        self.section_separator = parameters.get("section_separator")
        self.record_separator = parameters.get("record_separator", "\n")
        self.field_separator = parameters.get("field_separator")
        self.other_separator = parameters.get("other_separator")
        self.text_qualifier = parameters.get("text_qualifier")
        self.error_format = parameters.get("error_format")
        
        # Parse numeric parameters
        section_identity_column_index = parameters.get("section_identity_column_index")
        if section_identity_column_index:
            try:
                self.section_identity_column_index = int(section_identity_column_index.strip())
            except (ValueError, TypeError):
                pass
        
        # Parse boolean parameters
        self.ignore_blank_rows = parameters.get("ignore_blank_rows", "").lower() == "true"
        self.accept_trailing_white_space = parameters.get("accept_trailing_white_space", "").lower() == "true"
        self.allow_space_to_pad_numbers = parameters.get("allow_space_to_pad_numbers", "").lower() == "true"

    def get_parameter(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a parameter value."""
        return self.parameters.get(key, default)

    def get_section(self, section_index: str) -> Optional[Section]:
        """Get a section by index."""
        return self.sections.get(section_index)

    def get_columns_count(self, section_index: str) -> int:
        """Get the number of columns in a section."""
        section = self.get_section(section_index)
        return section.get_columns_count() if section else -1

    def get_column_rules(self, section_index: str, column_index: int) -> List[Rule]:
        """Get rules for a specific column in a section."""
        section = self.get_section(section_index)
        return section.get_rules(column_index) if section else []

    def get_column_alias(self, section_index: str, column_index: int) -> Optional[str]:
        """Get the alias for a specific column in a section."""
        rules = self.get_column_rules(section_index, column_index)
        for rule in rules:
            if rule.column_alias:
                return rule.column_alias
        return None

    def get_section_length(self, section_index: str) -> int:
        """Get the length of a section."""
        section = self.get_section(section_index)
        return section.length if section else 0

    def get_text_format_for_section(self, section_index: str) -> Optional[str]:
        """Get the text format for a section."""
        section = self.get_section(section_index)
        return section.section_format if section else None

    def get_column_checks(self, section_index: str, column_index: int) -> List[Rule]:
        """Get validation checks for a specific column in a section."""
        return self.get_column_rules(section_index, column_index)


@dataclass
class Message:
    """Represents a validation message."""
    text: str
    section_index: Optional[str] = None
    column_index: Optional[int] = None
    record_index: Optional[int] = None
    severity: Any = field(default_factory=lambda: MessageSeverity.ERROR)
    code: Optional[str] = None
    value: Optional[str] = None
    is_error: bool = True
    column_alias: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        severity_str = self.severity.value if hasattr(self.severity, 'value') else str(self.severity)
        return f"{self.text} [section={self.section_index}, column={self.column_index}, record={self.record_index}, severity={severity_str}]"


@dataclass
class RuleResult:
    """Result of applying a rule to a field."""
    rule: Optional[Rule] = None
    value: Optional[str] = None
    is_valid: bool = True
    message: Optional[Message] = None
    
    @property
    def has_error(self) -> bool:
        """Check if the result has an error."""
        return not self.is_valid and self.message and self.message.is_error
    
    @property
    def has_warning(self) -> bool:
        """Check if the result has a warning."""
        return self.is_valid and self.message and not self.message.is_error
    
    def add_message(self, message: Message) -> None:
        """Add a message to the result."""
        self.message = message
        if message.is_error:
            self.is_valid = False
    
    def __str__(self) -> str:
        msg_str = f", message={self.message}" if self.message else ""
        return f"RuleResult(rule={self.rule}, value={self.value}, valid={self.is_valid}{msg_str})"


@dataclass
class CellId:
    """Identifier for a cell in a flat file."""
    section_index: str
    column_index: int
    
    def __str__(self) -> str:
        return f"{self.section_index}:{self.column_index}" 