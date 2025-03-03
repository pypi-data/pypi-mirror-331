"""
Factory for creating processors.
"""
import logging
from typing import Dict, Type, Optional, Any

from .processors import (
    ProcessorAdapter, PropertiesToMapCopier, RecordCounter,
    TextAppender, BaseFormatConverter
)
from .models import FileProperties

# Set up logging
logger = logging.getLogger(__name__)


class ProcessorFactory:
    """Factory for creating processors."""
    
    _processors: Dict[str, Type[ProcessorAdapter]] = {
        "properties_to_map_copier": PropertiesToMapCopier,
        "record_counter": RecordCounter,
        "text_appender": TextAppender,
        "base_format_converter": BaseFormatConverter
    }
    
    @classmethod
    def get_processor(cls, processor_type: str, file_props: FileProperties,
                     total_records: int = -1) -> Optional[ProcessorAdapter]:
        """Get a processor by type."""
        processor_class = cls._processors.get(processor_type)
        if not processor_class:
            logger.warning(f"Processor type '{processor_type}' not found")
            return None
        
        processor = processor_class()
        processor.initialize(file_props, total_records)
        return processor
    
    @classmethod
    def register_processor(cls, processor_type: str, processor_class: Type[ProcessorAdapter]) -> None:
        """Register a processor."""
        cls._processors[processor_type] = processor_class 