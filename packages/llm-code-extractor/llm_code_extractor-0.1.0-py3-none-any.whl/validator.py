import re
import logging
from abc import ABC, abstractmethod
from .exceptions import LLMOutputException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutputValidator(ABC):
    """Abstract base class for LLM output validation."""
    
    @abstractmethod
    def validate(self, text: str) -> re.Match:
        pass

class LLMOutputValidator(OutputValidator):
    """Validates LLM-generated code output format."""

    LLM_PATTERN = re.compile(r"```(\w+)\s+//([\w\d_-]+\.\w+)\s+(.*?)```", re.DOTALL)

    def validate(self, text: str) -> re.Match:
        """Validates format and returns match object."""
        match = self.LLM_PATTERN.match(text)
        if not match:
            logger.warning("Invalid LLM output format detected.")
            raise LLMOutputException("Invalid LLM output format.")
        return match
