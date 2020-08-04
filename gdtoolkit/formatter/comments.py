import re
from typing import List, Optional

from lark import Tree

from ..parser import parser


def gather_standalone_comments(
    gdscript_code: str, comment_parse_tree: Tree
) -> List[Optional[str]]:
    comments = _gather_comments_by_regex(
        gdscript_code, comment_parse_tree, r"^\s*(#.*)$"
    )
    return _rstrip_comments(comments)


def gather_inline_comments(
    gdscript_code: str, comment_parse_tree: Tree
) -> List[Optional[str]]:
    comments = _gather_comments_by_regex(
        gdscript_code, comment_parse_tree, r"^\s*[^\s#]+[^#]*(#.*)$"
    )
    return _rstrip_comments(comments)


def _gather_comments_by_regex(
    gdscript_code: str, comment_parse_tree: Tree, comment_regex: str
) -> List[Optional[str]]:
    comment_line_numbers = [comment.line for comment in comment_parse_tree.children]
    lines = gdscript_code.splitlines()
    comments = [None]  # type: List[Optional[str]]
    regex = re.compile(comment_regex)
    for line_number, line in enumerate(lines):
        normalized_line_number = line_number + 1
        match = regex.search(line)
        if match is not None and normalized_line_number in comment_line_numbers:
            comments.append(match.group(1))
        else:
            comments.append(None)
    return comments


def gather_comments_from_code(
    gdscript_code: str, comment_tree: Optional[Tree] = None
) -> List[str]:
    comment_tree = (
        comment_tree
        if comment_tree is not None
        else parser.parse_comments(gdscript_code)
    )
    comment_line_numbers = [comment.line for comment in comment_tree.children]
    lines = gdscript_code.splitlines()
    comments = []  # type: List[str]
    for line_number, line in enumerate(lines):
        normalized_line_number = line_number + 1
        comment_start = line.find("#")
        if comment_start >= 0 and normalized_line_number in comment_line_numbers:
            comments.append(line[comment_start:])
    return comments


def _rstrip_comments(comments: List[Optional[str]]) -> List[Optional[str]]:
    return [
        comment.rstrip() if isinstance(comment, str) else comment
        for comment in comments
    ]
