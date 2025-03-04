"""
Factory for creating processors.
"""
import logging
from typing import Dict, Type, Optional, Any, TextIO

from .processors import (
    ProcessorAdapter, PropertiesToMapCopier, RecordCounter,
    TextAppender, BaseFormatConverter
)
from .processor import ValidationProcessor
from .models import FileProperties

# Set up logging
logger = logging.getLogger(__name__)


class ProcessorFactory:
    """Factory for creating processors."""
    
    _processors: Dict[str, Type[ProcessorAdapter]] = {
        "properties_to_map_copier": PropertiesToMapCopier,
        "properties_to_map": PropertiesToMapCopier,  # Alias for backward compatibility
        "record_counter": RecordCounter,
        "text_appender": TextAppender,
        "format_converter": BaseFormatConverter,
        "validator": ValidationProcessor
    }
    
    @classmethod
    def get_processor(cls, processor_type: str, file_props: FileProperties,
                     out_stream: Optional[TextIO] = None, 
                     error_stream: Optional[TextIO] = None,
                     buffer_size: int = 8192,
                     total_records: int = -1) -> Optional[ProcessorAdapter]:
        """Get a processor by type.
        
        Args:
            processor_type: The type of processor to create
            file_props: The file properties
            out_stream: The output stream
            error_stream: The error stream
            buffer_size: The buffer size for processing
            total_records: The total number of records (default: -1)
            
        Returns:
            The processor instance or None if the processor type is not found
        """
        processor_class = cls._processors.get(processor_type)
        if not processor_class:
            logger.warning(f"Processor type '{processor_type}' not found")
            return None
        
        # Special handling for ValidationProcessor which has a different constructor
        if processor_type == "validator":
            processor = processor_class(file_props, buffer_size=buffer_size)
            # Set streams if available
            if hasattr(processor, 'set_out_stream') and out_stream:
                processor.set_out_stream(out_stream)
            if hasattr(processor, 'set_error_stream') and error_stream:
                processor.set_error_stream(error_stream)
            return processor
        
        # Standard initialization for other processors
        processor = processor_class()
        processor.initialize(file_props, total_records)
        
        # Set additional properties if the processor supports them
        if hasattr(processor, 'set_out_stream') and out_stream:
            processor.set_out_stream(out_stream)
        
        if hasattr(processor, 'set_error_stream') and error_stream:
            processor.set_error_stream(error_stream)
            
        if hasattr(processor, 'set_buffer_size'):
            processor.set_buffer_size(buffer_size)
            
        return processor
    
    @classmethod
    def register_processor(cls, processor_type: str, processor_class: Type[ProcessorAdapter]) -> None:
        """Register a processor."""
        cls._processors[processor_type] = processor_class 