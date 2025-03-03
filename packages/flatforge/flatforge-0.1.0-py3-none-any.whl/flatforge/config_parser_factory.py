"""
Configuration parser factory for FlatForge.
"""
import os
from typing import Optional

from .config_parser import StringConfigParser
from .yaml_config_parser import YamlConfigParser


class ConfigParserFactory:
    """Factory for creating configuration parsers."""
    
    @staticmethod
    def get_config_parser(config_path: str):
        """
        Get a configuration parser based on the file extension.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            An appropriate configuration parser instance
            
        Raises:
            ValueError: If the file extension is not supported
        """
        _, ext = os.path.splitext(config_path)
        ext = ext.lower()
        
        if ext == '.txt':
            return StringConfigParser()
        elif ext in ('.yml', '.yaml'):
            return YamlConfigParser()
        else:
            raise ValueError(f"Unsupported configuration file extension: {ext}")
    
    @staticmethod
    def get_config_parser_by_type(config_type: str):
        """
        Get a configuration parser based on the type.
        
        Args:
            config_type: Type of configuration parser ('text' or 'yaml')
            
        Returns:
            An appropriate configuration parser instance
            
        Raises:
            ValueError: If the configuration type is not supported
        """
        if config_type == 'text':
            return StringConfigParser()
        elif config_type == 'yaml':
            return YamlConfigParser()
        else:
            raise ValueError(f"Unsupported configuration type: {config_type}") 