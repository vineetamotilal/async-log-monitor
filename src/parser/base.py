from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field

class LogEntry(BaseModel):
    """
    Core Pydantic model for structured log data.
    Specific implementations should extend this or create custom ones.
    """
    raw_content: str = Field(description="The original unparsed log line")
    timestamp: Optional[str] = Field(default=None, description="Extracted timestamp string")
    level: str = Field(default="INFO", description="Log level like INFO, ERROR, WARNING")
    is_error: bool = Field(default=False, description="Flag indicating if this line represents an error")
    extra_data: dict[str, Any] = Field(default_factory=dict, description="Any additional extracted fields")

class LogParserABC(ABC):
    """
    Abstract Base Class for Log Parsers.
    
    This fulfills the Dependency Inversion Principle. The reading engine focuses on feeding strings
    into the parse method without needing to know implementation details of the underlying format
    (e.g., Nginx access log, Apache error log, JSON app log).
    """

    @abstractmethod
    def parse(self, line: str) -> Optional[LogEntry]:
        """
        Parses a single raw string into a structured Pydantic model.
        
        Args:
            line: A raw line read from the log.
            
        Returns:
            A validated LogEntry model, or None if the line is not relevant/empty.
        """
        pass

    @abstractmethod
    def handles_format(self, sample_line: str) -> bool:
        """
        Predicate to check if this parser is capable of handling the log format.
        Useful for auto-detecting formats.
        
        Args:
            sample_line: A single line for introspection.
            
        Returns:
            True if compatible, False otherwise.
        """
        pass
