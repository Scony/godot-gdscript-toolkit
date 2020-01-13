from typing import List

from .constants import INDENT_STRING, INDENT_SIZE


# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
class Context:
    def __init__(
        self,
        indent: int,
        previously_processed_line_number: int,
        max_line_length: int,
        gdscript_code_lines: List,
        standalone_comments: List,
        inline_comments: List,
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
