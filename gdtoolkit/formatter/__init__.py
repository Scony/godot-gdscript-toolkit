import re
from typing import List

from lark import Tree

from ..parser import parser


class Context:
    def __init__(
        self,
        indent: int,
        previously_processed_line_number: int,
        gdscript_code_lines: List,
        comments: List,
    ):
        self.indent = indent
        self.previously_processed_line_number = previously_processed_line_number
        self.gdscript_code_lines = gdscript_code_lines
        self.comments = comments


def format_code(gdscript_code: str, max_line_length: int) -> str:
    assert max_line_length > 0
    parse_tree = parser.parse(gdscript_code, gather_metadata=True)
    gdscript_code_lines = [None] + gdscript_code.splitlines()
    comments = _gather_comments_from_code(gdscript_code)
    formatted_lines = []
    previously_processed_line_number = 0
    context = Context(
        indent=0,
        previously_processed_line_number=previously_processed_line_number,
        gdscript_code_lines=gdscript_code_lines,
        comments=comments,
    )
    formatted_lines, _ = _format_class_body(parse_tree.children, context)
    formatted_lines.append("")
    return "\n".join(formatted_lines)


def _format_class_body(statements: List, context: Context) -> (List[str], int):
    formatted_lines = []
    previously_processed_line_number = context.previously_processed_line_number
    for statement in statements:
        formatted_lines += _reconstruct_blank_lines_in_range(
            previously_processed_line_number, statement.line, context,
        )
        previously_processed_line_number = statement.line
        if statement.data == "tool_stmt":
            formatted_lines.append("{}tool".format(" " * context.indent))
        elif statement.data == "class_def":
            name = statement.children[0].value
            formatted_lines.append("{}class {}:".format(" " * context.indent, name))
            class_lines, last_processed_line = _format_class_body(
                statement.children[1:],
                Context(
                    indent=context.indent + 4,
                    previously_processed_line_number=previously_processed_line_number,
                    gdscript_code_lines=context.gdscript_code_lines,
                    comments=context.comments,
                ),
            )
            formatted_lines += class_lines
            previously_processed_line_number = last_processed_line
        if context.comments[statement.line] is not None:
            formatted_lines[-1] = "{}  {}".format(
                formatted_lines[-1], context.comments[statement.line]
            )
    dedent_line_number = _find_dedent_line_number(
        previously_processed_line_number, context
    )
    formatted_lines += _reconstruct_blank_lines_in_range(
        previously_processed_line_number, dedent_line_number, context,
    )
    previously_processed_line_number = dedent_line_number - 1
    return (formatted_lines, previously_processed_line_number)


def _find_dedent_line_number(previously_processed_line_number: int, context: Context):
    if previously_processed_line_number == len(context.gdscript_code_lines) - 1:
        return len(context.gdscript_code_lines)
    line_no = previously_processed_line_number + 1
    for line in context.gdscript_code_lines[previously_processed_line_number + 1 :]:
        if re.search(r"^ {0,%d}[^ ]+" % (context.indent - 1), line) is not None:
            return line_no
        line_no += 1
    return line_no


def _gather_comments_from_code(gdscript_code: str) -> List[str]:
    lines = gdscript_code.splitlines()
    comments = [None] * (len(lines) + 1)
    for i, line in enumerate(lines):
        comment_start = line.find("#")
        if comment_start >= 0:
            comments[i + 1] = line[comment_start:]
    return comments


def _reconstruct_blank_lines_in_range(
    begin: int, end: int, context: Context
) -> List[str]:
    comments = context.comments
    prefix = " " * context.indent
    comments_in_range = (
        comments[begin + 1 : end] if end != -1 else comments[begin + 1 :]
    )
    reconstructed_lines = ["" if c is None else prefix + c for c in comments_in_range]
    if begin == 0:
        reconstructed_lines = _remove_empty_strings_from_begin(reconstructed_lines)
    if end == -1:
        reconstructed_lines = list(
            reversed(
                _remove_empty_strings_from_begin(list(reversed(reconstructed_lines)))
            )
        )
    return reconstructed_lines


def _remove_empty_strings_from_begin(lst: List) -> List:
    for i, el in enumerate(lst):
        if el != "":
            return lst[i:]
    return []


def _blank_lines_between(begin: int, end: int) -> int:
    return end - (begin + 1)
