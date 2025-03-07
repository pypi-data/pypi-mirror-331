import pytest
from src.extractor import LLMCodeExtractor
from src.exceptions import LLMOutputException
import re

extractor = LLMCodeExtractor()

def test_extract_valid_code():
    input_string = "```python //example.py print('Hello')```"
    pattern = r"```(\w+)\s+//([\w\d_-]+\.\w+)\s+(.*?)```"
    match = re.search(pattern, input_string, re.DOTALL)
    assert match is not None, "Pattern did not match the input string."
    code_block = extractor.extract(match)
    assert code_block.filename == "example.py"
    assert code_block.extension == "py"
    assert code_block.code == "print('Hello')"


def test_filename_extension_mismatch():
    match = re.match(r"```(\w+)\s+//([\w\d_-]+\.\w+)\s+(.*?)```", "```python //example.js print('Hello')```", re.DOTALL)
    with pytest.raises(LLMOutputException):
        extractor.extract(match)
