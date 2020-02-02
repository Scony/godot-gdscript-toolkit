from typing import List, Optional
from dataclasses import dataclass

from .constants import INDENT_STRING, INDENT_SIZE


# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
class Context:
    def __init__(
        self,
        indent: int,
        previously_processed_line_number: int,
        max_line_length: int,
        gdscript_code_lines: List[str],
        standalone_comments: List[Optional[str]],
        inline_comments: List[Optional[str]],
    ):
        self.indent = indent
        self.previously_processed_line_number = previously_processed_line_number
        self.max_line_length = max_line_length
        self.gdscript_code_lines = gdscript_code_lines
        self.standalone_comments = standalone_comments
        self.inline_comments = inline_comments
        self.indent_string = INDENT_STRING * (self.indent // INDENT_SIZE)

    def create_child_context(self, previously_processed_line_number: int):
        return Context(
            indent=self.indent + INDENT_SIZE,
            previously_processed_line_number=previously_processed_line_number,
            max_line_length=self.max_line_length,
            gdscript_code_lines=self.gdscript_code_lines,
            standalone_comments=self.standalone_comments,
            inline_comments=self.inline_comments,
        )


# TODO: remove optional from suffix line and align codebase
@dataclass
class ExpressionContext:
    prefix_string: str
    prefix_line: int  # earliest line number of prefix string
    suffix_string: str
    suffix_line: Optional[int] = None  # earliest line number of suffix string
