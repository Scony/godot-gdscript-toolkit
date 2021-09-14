import re
from typing import List, Optional

from lark import Tree

from ..parser import parser
from .context import Context
from .constants import INLINE_COMMENT_OFFSET, GLOBAL_SCOPE_SURROUNDING_EMPTY_LINES_TABLE
from .types import FormattedLines
from .block import format_block
from .class_statement import format_class_statement
from .comments import (
    gather_standalone_comments,
    gather_inline_comments,
)

INDENT_REGEX = re.compile(r"^\t+")


def format_code(
    gdscript_code: str,
    max_line_length: int,
    parse_tree: Optional[Tree] = None,
    comment_parse_tree: Optional[Tree] = None,
) -> str:
    parse_tree = (
        parse_tree
        if parse_tree is not None
        else parser.parse(gdscript_code, gather_metadata=True)
    )
    comment_parse_tree = (
        comment_parse_tree
        if comment_parse_tree is not None
        else parser.parse_comments(gdscript_code)
    )
    gdscript_code_lines = [
        "",
        *gdscript_code.splitlines(),
    ]  # type: List[str]
    formatted_lines = []  # type: FormattedLines
    context = Context(
        indent=0,
        previously_processed_line_number=0,
        max_line_length=max_line_length,
        gdscript_code_lines=gdscript_code_lines,
        standalone_comments=gather_standalone_comments(
            gdscript_code, comment_parse_tree
        ),
        inline_comments=gather_inline_comments(gdscript_code, comment_parse_tree),
    )
    formatted_lines, _ = format_block(
        parse_tree.children,
        format_class_statement,
        context,
        GLOBAL_SCOPE_SURROUNDING_EMPTY_LINES_TABLE,
    )
    formatted_lines.append((None, ""))
    formatted_lines = _add_inline_comments(formatted_lines, context.inline_comments)
    formatted_lines = _add_standalone_comments(
        formatted_lines, context.standalone_comments
    )
    return "\n".join([line for _, line in formatted_lines])


def _add_inline_comments(
    formatted_lines: FormattedLines, comments: List[Optional[str]]
) -> FormattedLines:
    remaining_comments = comments[:]
    postprocessed_lines = []  # type: FormattedLines
    comment_offset = " " * INLINE_COMMENT_OFFSET

    for line_no, line in reversed(formatted_lines):
        if line_no is None:
            postprocessed_lines.append((line_no, line))
            continue
        comments = remaining_comments[line_no:]
        remaining_comments = remaining_comments[:line_no]
        if comments != []:
            new_line = comment_offset.join(
                [line] + [c for c in comments if c is not None]
            )
            postprocessed_lines.append((line_no, new_line))
        else:
            postprocessed_lines.append((line_no, line))

    return list(reversed(postprocessed_lines))


def _add_standalone_comments(
    formatted_lines: FormattedLines, standalone_comments: List[Optional[str]]
) -> FormattedLines:
    remaining_comments = standalone_comments[:]
    postprocessed_lines = []  # type: FormattedLines
    currently_inside_expression = False
    last_experssion_line_no = None

    for line_no, line in reversed(formatted_lines):
        if line_no is None:
            postprocessed_lines.append((line_no, line))
            currently_inside_expression = False
            continue
        if not currently_inside_expression:
            postprocessed_lines.append((line_no, line))
            currently_inside_expression = True
            last_experssion_line_no = line_no
            continue
        comments = remaining_comments[line_no:last_experssion_line_no]
        remaining_comments = remaining_comments[:line_no]
        indent = _get_greater_indent(line, postprocessed_lines[-1][1])
        postprocessed_lines += [
            (None, f"{indent}{comment}")
            for comment in reversed(comments)
            if comment is not None
        ]
        postprocessed_lines.append((line_no, line))

    return list(reversed(postprocessed_lines))


def _get_greater_indent(line_a: str, line_b: str):
    line_a_match = INDENT_REGEX.search(line_a)
    line_b_match = INDENT_REGEX.search(line_b)
    line_a_indent = "" if line_a_match is None else line_a_match.group(0)
    line_b_indent = "" if line_b_match is None else line_b_match.group(0)
    return line_a_indent if len(line_a_indent) > len(line_b_indent) else line_b_indent
