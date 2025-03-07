from abc import ABC, abstractmethod
from .exceptions import LLMOutputException
from collections import namedtuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CodeBlock = namedtuple("CodeBlock", ["filename", "extension", "code"])

LANGUAGE_EXTENSION_MAP = {
    'python': 'py',
    'javascript': 'js',
    'java': 'java',
    'csharp': 'cs',
    'ruby': 'rb',
    'php': 'php',
    'c': 'c',
    'cpp': 'cpp',
    # Add more mappings as needed
}

class CodeExtractor(ABC):
    """Abstract base class for extracting details from LLM output."""

    @abstractmethod
    def extract(self, match) -> CodeBlock:
        pass

class LLMCodeExtractor(CodeExtractor):
    """Extracts filename, extension, and code content."""

    def extract(self, match) -> CodeBlock:
        language_identifier, filename, code_content = match.groups()
        expected_extension = LANGUAGE_EXTENSION_MAP.get(language_identifier.lower())

        if expected_extension is None:
            logger.error(f"Unrecognized language identifier '{language_identifier}'.")
            raise LLMOutputException("Unrecognized language identifier.")

        if not filename.endswith(f".{expected_extension}"):
            logger.error(
                f"Filename '{filename}' does not end with the expected extension '.{expected_extension}' "
                f"for language '{language_identifier}'."
            )
            raise LLMOutputException("Filename and language identifier mismatch.")

        return CodeBlock(filename=filename, extension=expected_extension, code=code_content.strip())
