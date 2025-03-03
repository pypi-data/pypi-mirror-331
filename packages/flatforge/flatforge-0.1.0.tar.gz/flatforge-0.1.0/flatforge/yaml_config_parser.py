"""
YAML configuration parser for FlatForge.
"""
import logging
from typing import Dict, List, Any, Optional, Union
import yaml

from .models import Rule, GlobalRule, Section, FileProperties
from .config_parser import ConfigParser


# Set up logging
logger = logging.getLogger(__name__)


class YamlConfigParser(ConfigParser):
    """Parser for YAML-based configuration files."""
    
    def parse(self, obj: Union[str, dict]) -> FileProperties:
        """Parse a YAML configuration into a FileProperties object."""
        # Parse YAML string to dictionary
        try:
            if isinstance(obj, str):
                config_dict = yaml.safe_load(obj)
            elif isinstance(obj, dict):
                config_dict = obj
            else:
                raise ValueError(f"Expected string or dictionary, got {type(obj)}")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise ValueError(f"Invalid YAML configuration: {e}")
        
        # Create a new FileProperties object
        file_props = FileProperties()
        
        # Extract parameters
        parameters = {}
        # Copy basic parameters
        for key in ['delimiter', 'encoding', 'text_format_code', 'section_separator', 
                   'record_separator', 'field_separator', 'text_qualifier']:
            if key in config_dict:
                parameters[key] = config_dict[key]
        
        # Add any other parameters
        if 'parameters' in config_dict:
            parameters.update(config_dict['parameters'])
            
        file_props.set_parameters(parameters)
        
        # Extract sections
        sections_dict = config_dict.get('section_metadata', {})
        sections = {}
        global_rules = []
        
        for section_index, section_data in sections_dict.items():
            section = self._parse_section(section_index, section_data)
            sections[section_index] = section
            
            # Collect global rules from section
            for column_rules in section.rules.values():
                for rule in column_rules:
                    if isinstance(rule, GlobalRule):
                        global_rules.append(rule)
        
        file_props.sections = sections
        file_props.global_rules = global_rules
        
        return file_props
    
    def _parse_section(self, section_index: str, section_data: Any) -> Section:
        """Parse a section from YAML data."""
        # Check if section_data is a dictionary
        if not isinstance(section_data, dict):
            raise ValueError(f"Invalid section format for section {section_index}: expected dictionary, got {type(section_data)}")
            
        # Handle format field
        format_data = section_data.get('format', {})
        section_format = None
        length = 0
        
        if isinstance(format_data, dict):
            format_type = format_data.get('type', '').upper()
            
            if format_type == 'FL':
                # Fixed length format
                lengths = format_data.get('lengths', [])
                if lengths:
                    section_format = f"fl{{{','.join(str(l) for l in lengths)}}}"
                    length = sum(lengths)
                else:
                    section_format = "fl"
            elif format_type == 'DEL':
                # Delimited format
                section_format = "del"
            else:
                section_format = format_type.lower()
        else:
            section_format = str(format_data).lower()
        
        # Create a new section
        section = Section(
            index=section_index,
            section_format=section_format,
            length=length
        )
        
        # Parse column rules
        columns_data = section_data.get('columns', [])
        column_rules = {}
        
        # Handle list-style columns
        if isinstance(columns_data, list):
            for column_index, column_data in enumerate(columns_data):
                rules = []
                
                if isinstance(column_data, dict) and 'rules' in column_data:
                    for rule_data in column_data.get('rules', []):
                        rule = self._parse_rule(rule_data)
                        
                        # Check if this is a global rule
                        if isinstance(rule_data, dict) and rule_data.get('is_global', False):
                            global_rule = self._parse_global_rule(rule, section_index, column_index, rule_data)
                            rules.append(global_rule)
                        # Check for cr_unique rule which is always global
                        elif rule.name == 'cr_unique':
                            global_rule = GlobalRule(
                                name=rule.name,
                                parameters=rule.parameters,
                                section_index=section_index,
                                column_index=column_index,
                                column_alias=rule.column_alias,
                                is_optional=rule.is_optional
                            )
                            rules.append(global_rule)
                        else:
                            rules.append(rule)
                
                if rules:
                    column_rules[column_index] = rules
        # Handle dictionary-style columns
        else:
            for column_index_str, rules_data in columns_data.items():
                try:
                    column_index = int(column_index_str)
                except ValueError:
                    logger.warning(f"Invalid column index: {column_index_str}")
                    continue
                
                rules = []
                
                for rule_data in rules_data:
                    rule = self._parse_rule(rule_data)
                    
                    # Check if this is a global rule
                    if isinstance(rule_data, dict) and rule_data.get('is_global', False):
                        global_rule = self._parse_global_rule(rule, section_index, column_index, rule_data)
                        rules.append(global_rule)
                    # Check for cr_unique rule which is always global
                    elif rule.name == 'cr_unique':
                        global_rule = GlobalRule(
                            name=rule.name,
                            parameters=rule.parameters,
                            section_index=section_index,
                            column_index=column_index,
                            column_alias=rule.column_alias,
                            is_optional=rule.is_optional
                        )
                        rules.append(global_rule)
                    else:
                        rules.append(rule)
                
                column_rules[column_index] = rules
        
        section.rules = column_rules
        
        # Parse instructions
        instructions = []
        for instruction_data in section_data.get('instructions', []):
            instruction = self._parse_rule(instruction_data)
            instructions.append(instruction)
        
        section.instructions = instructions
        
        return section
    
    def _parse_rule(self, rule_data: Any) -> Rule:
        """Parse a rule from YAML data."""
        # Handle string rule format (just the rule name)
        if isinstance(rule_data, str):
            return Rule(name=rule_data)
            
        # Handle dictionary rule format
        if isinstance(rule_data, dict):
            name = rule_data.get('name', '')
            
            # Handle parameters
            parameters = rule_data.get('parameters', [])
            # Convert single parameter to list
            if parameters and not isinstance(parameters, list):
                if isinstance(parameters, str):
                    parameters = [parameters]
                else:
                    parameters = [str(parameters)]
                    
            column_alias = rule_data.get('column_alias')
            is_optional = rule_data.get('is_optional', False)
            
            return Rule(
                name=name,
                parameters=parameters,
                column_alias=column_alias,
                is_optional=is_optional
            )
            
        # Default case
        logger.warning(f"Unexpected rule data format: {type(rule_data)}")
        return Rule(name=str(rule_data))
    
    def _parse_global_rule(self, rule: Rule, section_index: str, column_index: int, rule_data: Dict) -> GlobalRule:
        """Parse a global rule from YAML data."""
        global_rule = GlobalRule(
            name=rule.name,
            parameters=rule.parameters,
            section_index=section_index,
            column_index=column_index,
            column_alias=rule.column_alias,
            is_optional=rule.is_optional
        )
        
        # Set additional global rule properties if they exist in rule_data
        if hasattr(rule_data, 'get'):
            global_rule.read_start_index = rule_data.get('read_start_index', -1)
            global_rule.read_end_index = rule_data.get('read_end_index', -1)
            global_rule.write_start_index = rule_data.get('write_start_index', -1)
            global_rule.write_end_index = rule_data.get('write_end_index', -1)
            global_rule.action = rule_data.get('action')
        
        return global_rule 