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
    formatted_lines_with_inlined_comments = _add_inline_comments(
        formatted_lines, context.inline_comments
    )
    return "\n".join([line for _, line in formatted_lines_with_inlined_comments])


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
