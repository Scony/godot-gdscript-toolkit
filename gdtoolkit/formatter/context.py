import re
from typing import List, Optional
from types import MappingProxyType
from dataclasses import dataclass

from lark import Tree
from .constants import DEFAULT_SURROUNDING_EMPTY_LINES_TABLE


# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-positional-arguments
class Context:
    def __init__(
        self,
        previously_processed_line_number: int,
        single_indent_size: int,
        single_indent_string: str,
        max_line_length: int,
        global_surrounding_empty_lines_table: MappingProxyType,
        gdscript_code_lines: List[str],
        standalone_comments: List[Optional[str]],
        inline_comments: List[Optional[str]],
        indent: int = 0,
    ):
        self.single_indent = single_indent_size
        self.single_indent_string = single_indent_string
        self.indent = indent
        self.indent_string = self.single_indent_string * (
            self.indent // self.single_indent
        )
        self.indent_regex = re.compile(f"^{self.single_indent_string[0]}+")
        self.previously_processed_line_number = previously_processed_line_number
        self.max_line_length = max_line_length
        self.global_surrounding_empty_lines_table = global_surrounding_empty_lines_table
        self.gdscript_code_lines = gdscript_code_lines
        self.standalone_comments = standalone_comments
        self.inline_comments = inline_comments
        self.annotations = []  # type: List[Tree]

    def create_child_context(self, previously_processed_line_number: int):
        return Context(
            single_indent_size=self.single_indent,
            single_indent_string=self.single_indent_string,
            previously_processed_line_number=previously_processed_line_number,
            max_line_length=self.max_line_length,
            global_surrounding_empty_lines_table=self.global_surrounding_empty_lines_table,
            gdscript_code_lines=self.gdscript_code_lines,
            standalone_comments=self.standalone_comments,
            inline_comments=self.inline_comments,
            indent=self.indent + self.single_indent,
        )

    def surrounding_empty_lines_for_scope(self):
        return (
            self.global_surrounding_empty_lines_table
            if self.indent == 0
            else DEFAULT_SURROUNDING_EMPTY_LINES_TABLE
        )


@dataclass
class ExpressionContext:
    prefix_string: str
    prefix_line: int  # earliest line number of prefix string
    suffix_string: str
    suffix_line: int  # earliest line number of suffix string
