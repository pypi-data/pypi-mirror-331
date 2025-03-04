"""
FlatForge

A utility for validating and processing flat files (text files with structured data).
"""

from .config_parser import StringConfigParser
from .yaml_config_parser import YamlConfigParser
from .config_parser_factory import ConfigParserFactory
from .processor import ValidationProcessor, ValidatorFactory
from .models import (
    Rule, GlobalRule, Section, FileProperties,
    Message, RuleResult, CellId, MessageSeverity
)
from .validators import (
    ValidationContext, NumberValidator, StringValidator, ChoiceValidator, 
    DateValidator, IChoiceValidator, PrefixValidator, SuffixValidator,
    PutValidator, TrimValidator, UniqueValidator, SumCrValidator, CountCrValidator
)
from .utils import (
    TextFormat, FlatFileError, ValidationError, ConfigurationError,
    is_blank, is_not_blank, contains_ignore_case, contains_ignore_case_list
)

__version__ = "0.1.0" 