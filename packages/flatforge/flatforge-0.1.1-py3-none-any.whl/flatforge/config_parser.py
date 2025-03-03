"""
Configuration parser for FlatForge.
"""
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
import re

from .models import Rule, GlobalRule, Section, FileProperties
from .utils import StringUtils, ConfigParserUtil, TextFormat


# Set up logging
logger = logging.getLogger(__name__)


class ConfigParser:
    """Base class for configuration parsers."""
    
    def parse(self, obj: Any) -> FileProperties:
        """Parse a configuration object into a FileProperties object."""
        raise NotImplementedError("Subclasses must implement parse()")


class StringConfigParser:
    """Parser for string-based configuration files."""
    
    KEY_SECTION = "section_metadata"
    CR_PREFIX = "cr_"
    
    def __init__(self):
        """Initialize the parser."""
        self.cr_rules = []
        self.sections = {}
    
    def parse(self, obj: str) -> FileProperties:
        """Parse a string configuration into a FileProperties object."""
        # Reset cross-record rules list
        self.cr_rules = []
        self.sections = {}
        
        # Create a new FileProperties object
        file_props = FileProperties()
        
        # Split the configuration into sections
        sections = {}
        parameters = {}
        
        # Parse the configuration string
        lines = obj.strip().split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Check if this is a section header
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].strip()
                continue
            
            # Skip lines without a current section
            if current_section is None:
                continue
            
            # Parse parameters section
            if current_section == "parameters":
                if "=" in line:
                    key, value = line.split("=", 1)
                    parameters[key.strip()] = value.strip()
            
            # Parse section metadata
            elif current_section == self.KEY_SECTION:
                if "=" in line:
                    key, value = line.split("=", 1)
                    section_index = key.strip()
                    section = self.parse_section(section_index, value.strip(), "|")
                    sections[section_index] = section
                    self.sections[section_index] = section
        
        # Set parameters and sections
        file_props.set_parameters(parameters)
        file_props.sections = sections
        
        # Assign collected cross-record rules
        file_props.global_rules = self.cr_rules
        
        # Validate the metadata
        self.validate_metadata(file_props)
        
        return file_props
    
    def parse_section(self, section_index: str, raw_record: str, field_separator: str) -> Section:
        """Parse a section from a raw record string."""
        parts = raw_record.split(field_separator)
        
        # Create a new section
        section = Section(index=section_index)
        
        # Parse the section format
        if parts and parts[0].startswith("fl{"):
            section.section_format = TextFormat.FIXED_LENGTH.value
            # Extract column lengths
            match = re.search(r"fl\{(.*?)\}", parts[0])
            if match:
                lengths = match.group(1).split(",")
                section.length = sum(int(length.strip()) for length in lengths if length.strip().isdigit())
        
        # Parse column rules
        for i in range(1, len(parts)):
            part = parts[i]
            if ":" in part:
                column_index_str, rule_str = part.split(":", 1)
                try:
                    column_index = int(column_index_str)
                    
                    # Parse rules for this column
                    rules = []
                    if "," in rule_str:
                        rule_parts = rule_str.split(",")
                    else:
                        rule_parts = [rule_str]
                    
                    for rule_part in rule_parts:
                        # Check for column alias
                        column_alias = None
                        if ":" in rule_part:
                            rule_part, column_alias = rule_part.split(":", 1)
                        
                        # Check for optional flag
                        is_optional = False
                        if rule_part.endswith("?"):
                            is_optional = True
                            rule_part = rule_part[:-1]
                        
                        # Parse the rule
                        rule = self.parse_rule(rule_part)
                        rule.column_alias = column_alias
                        rule.is_optional = is_optional
                        
                        # Check if this is a global rule
                        if self.is_cr_rule(rule):
                            cr_rule = self.parse_global_rule(rule, section_index, column_index)
                            rules.append(cr_rule)
                            self.cr_rules.append(cr_rule)
                        else:
                            rules.append(rule)
                    
                    # Add rules to the section
                    if column_index not in section.rules:
                        section.rules[column_index] = []
                    section.rules[column_index].extend(rules)
                except ValueError:
                    # Skip invalid column indices
                    pass
        
        return section
    
    def is_cr_rule(self, rule: Rule) -> bool:
        """Check if a rule is a cross-record rule."""
        return rule.name.startswith(self.CR_PREFIX)
    
    def parse_global_rule(self, rule: Rule, section_index: str, column_index: int) -> GlobalRule:
        """Parse a global rule from a regular rule."""
        return GlobalRule(
            name=rule.name,
            parameters=rule.parameters,
            section_index=section_index,
            column_index=column_index,
            column_alias=rule.column_alias,
            is_optional=rule.is_optional
        )
    
    def parse_rule(self, instruction: str) -> Rule:
        """Parse a rule from an instruction string."""
        # Extract rule name and parameters
        name = instruction
        parameters = []
        
        # Check if the rule has parameters
        if "(" in instruction and instruction.endswith(")"):
            name, params_str = instruction.split("(", 1)
            params_str = params_str.rstrip(")")
            parameters = [p.strip() for p in params_str.split(",")]
        
        # Create the rule
        return Rule(
            name=name,
            parameters=parameters
        )
    
    def validate_metadata(self, file_props: FileProperties) -> bool:
        """Validate the file properties."""
        # Update sections from file_props
        self.sections = file_props.sections
        
        # Validate global rules
        for rule in file_props.global_rules:
            if not self.validate_global_rule(rule):
                raise ValueError(f"Invalid global rule: {rule}")
        
        return True
    
    def validate_global_rule(self, rule: GlobalRule) -> bool:
        """Validate a global rule."""
        # Check if the referenced section exists
        if rule.section_index not in self.sections:
            return False
        
        # Check if the referenced column exists
        section = self.sections.get(rule.section_index)
        if section and rule.column_index not in section.rules:
            return False
        
        return True 