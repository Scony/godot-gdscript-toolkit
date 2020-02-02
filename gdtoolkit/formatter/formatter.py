import re
from typing import List, Optional

from ..parser import parser
from .context import Context
from .constants import INLINE_COMMENT_OFFSET, GLOBAL_SCOPE_SURROUNDING_EMPTY_LINES_TABLE
from .types import FormattedLines
from .block import format_block
from .class_statement import format_class_statement


def format_code(gdscript_code: str, max_line_length: int) -> str:
    parse_tree = parser.parse(gdscript_code, gather_metadata=True)
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
        standalone_comments=_gather_standalone_comments_from_code(gdscript_code),
        inline_comments=_gather_inline_comments_from_code(gdscript_code),
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


def _gather_standalone_comments_from_code(gdscript_code: str) -> List[Optional[str]]:
    return _gather_comments_from_code_by_regex(gdscript_code, r"^\s*(#.*)$")


def _gather_inline_comments_from_code(gdscript_code: str) -> List[Optional[str]]:
    return _gather_comments_from_code_by_regex(gdscript_code, r"^\s*[^\s#]+[^#]*(#.*)$")


def _gather_comments_from_code_by_regex(
    gdscript_code: str, comment_regex: str
) -> List[Optional[str]]:
    lines = gdscript_code.splitlines()
    comments = [None]  # type: List[Optional[str]]
    regex = re.compile(comment_regex)
    for line in lines:
        match = regex.search(line)
        if match is not None:
            comments.append(match.group(1))
        else:
            comments.append(None)
    return comments


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
