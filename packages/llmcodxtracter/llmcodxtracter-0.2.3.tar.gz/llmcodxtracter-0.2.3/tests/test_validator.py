import pytest
from src.llmcodxtracter.validator import LLMOutputValidator
from src.llmcodxtracter.exceptions import LLMOutputException

validator = LLMOutputValidator()

def test_valid_output():
    text = "```python //example.py print('Hello, World!')```"
    assert validator.validate(text) is not None

def test_invalid_output():
    text = "This is not valid code block"
    with pytest.raises(LLMOutputException):
        validator.validate(text)
