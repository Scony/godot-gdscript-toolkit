import re
from typing import List, Optional, Dict

from lark import Tree

from ..parser import parser


def gather_comments(
    gdscript_code: str, comment_parse_tree: Optional[Tree] = None
) -> List[str]:
    comment_parse_tree = (
        comment_parse_tree
        if comment_parse_tree is not None
        else parser.parse_comments(gdscript_code)
    )
    return [comment.value.rstrip() for comment in comment_parse_tree.children]


def gather_standalone_comments(
    gdscript_code: str, comment_parse_tree: Tree
) -> List[Optional[str]]:
    comments = _gather_comments_by_prefix_regex(
        gdscript_code, comment_parse_tree, r"^\s*$"
    )
    return _rstrip_comments(comments)


def gather_inline_comments(
    gdscript_code: str, comment_parse_tree: Tree
) -> List[Optional[str]]:
    comments = _gather_comments_by_prefix_regex(
        gdscript_code, comment_parse_tree, r"[^\s]+"
    )
    return _rstrip_comments(comments)


def _gather_comments_by_prefix_regex(
    gdscript_code: str, comment_parse_tree: Tree, prefix_regex: str
) -> List[Optional[str]]:
    """prefix means all line characters before comment"""
    line_to_comment_mapping = {
        comment.line: comment for comment in comment_parse_tree.children
    }  # type: Dict[int, Tree]
    lines = gdscript_code.splitlines()
    comments = [None]  # type: List[Optional[str]]
    regex = re.compile(prefix_regex)
    for line_number, line in enumerate(lines):
        normalized_line_number = line_number + 1
        if normalized_line_number not in line_to_comment_mapping:
            comments.append(None)
            continue
        prefix = line[: line_to_comment_mapping[normalized_line_number].column - 1]
        match = regex.search(prefix)
        if match is None:
            comments.append(None)
        else:
            comments.append(line_to_comment_mapping[normalized_line_number].value)
    return comments


def _rstrip_comments(comments: List[Optional[str]]) -> List[Optional[str]]:
    return [
        comment.rstrip() if isinstance(comment, str) else comment
        for comment in comments
    ]
