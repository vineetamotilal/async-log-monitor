import json
from typing import Optional
from .base import LogParserABC, LogEntry

class JSONLogParser(LogParserABC):
    """
    A concrete implementation of LogParserABC that handles JSON-formatted log lines.
    """
    
    def parse(self, line: str) -> Optional[LogEntry]:
        try:
            data = json.loads(line)
            # Ensure it's a dict
            if not isinstance(data, dict):
                return None
            
            level = data.get("level", "INFO").upper()
            is_error = level in ("ERROR", "FATAL", "CRITICAL")
            
            return LogEntry(
                raw_content=line,
                timestamp=data.get("timestamp"),
                level=level,
                is_error=is_error,
                extra_data=data
            )
        except json.JSONDecodeError:
            return None

    def handles_format(self, sample_line: str) -> bool:
        try:
            json.loads(sample_line)
            return True
        except json.JSONDecodeError:
            return False
