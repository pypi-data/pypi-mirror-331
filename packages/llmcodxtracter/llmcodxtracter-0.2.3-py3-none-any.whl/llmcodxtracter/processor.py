from .validator import LLMOutputValidator
from .extractor import LLMCodeExtractor
from .exceptions import LLMOutputException
from collections import namedtuple

CodeBlock = namedtuple("CodeBlock", ["filename", "extension", "code"])

# Mapping programming languages to standard file extensions
LANGUAGE_TO_EXTENSION = {
    "python": "py",
    "javascript": "js",
    "typescript": "ts",
    "java": "java",
    "c": "c",
    "cpp": "cpp",
    "cs": "cs",  # C#
    "go": "go",
    "rust": "rs",
    "swift": "swift",
    "ruby": "rb",
    "php": "php",
    "html": "html",
    "css": "css",
    "json": "json",
    "yaml": "yaml",
}

class LLMOutputProcessor:
    """Processor for validating and extracting LLM-generated code output."""

    def __init__(self, validator: LLMOutputValidator, extractor: LLMCodeExtractor):
        self.validator = validator
        self.extractor = extractor

    def process(self, text: str):
        """Validates and extracts LLM output."""
        match = self.validator.validate(text)
        code_block = self.extractor.extract(match)

        # Standardize extension based on language name
        if code_block.extension in LANGUAGE_TO_EXTENSION:
            standardized_extension = LANGUAGE_TO_EXTENSION[code_block.extension]
        else:
            standardized_extension = code_block.extension  # Keep as is if not in mapping

        # Ensure filename and extension match
        filename = code_block.filename
        if not filename.endswith(f".{standardized_extension}"):
            filename = f"{filename.split('.')[0]}.{standardized_extension}"

        return CodeBlock(filename, standardized_extension, code_block.code)

# Instantiate components
validator = LLMOutputValidator()
extractor = LLMCodeExtractor()
processor = LLMOutputProcessor(validator, extractor)
