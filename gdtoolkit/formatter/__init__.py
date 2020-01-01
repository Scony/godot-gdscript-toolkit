from typing import List

from ..parser import parser


def format_code(gdscript_code: str, max_line_length: int) -> str:
    assert max_line_length > 0
    parse_tree = parser.parse(gdscript_code, gather_metadata=True)
    comments = _gather_comments_from_code(gdscript_code)
    formatted_lines = []
    previously_processed_line_number = 0
    for statement in parse_tree.children:
        formatted_lines += _reconstruct_blank_lines_in_range(
            previously_processed_line_number, statement.line, comments
        )
        previously_processed_line_number = statement.line
        if statement.data == "tool_stmt":
            formatted_lines.append("tool")
        if comments[statement.line] is not None:
            formatted_lines[-1] = "{}  {}".format(
                formatted_lines[-1], comments[statement.line]
            )
    formatted_lines += _reconstruct_blank_lines_in_range(
        previously_processed_line_number, -1, comments
    )
    formatted_lines.append("")
    return "\n".join(formatted_lines)


def _gather_comments_from_code(gdscript_code: str) -> List[str]:
    lines = gdscript_code.splitlines()
    comments = [None] * (len(lines) + 1)
    for i, line in enumerate(lines):
        comment_start = line.find("#")
        if comment_start >= 0:
            comments[i + 1] = line[comment_start:]
    return comments


def _reconstruct_blank_lines_in_range(
    begin: int, end: int, comments: List[str]
) -> List[str]:
    comments_in_range = (
        comments[begin + 1 : end] if end != -1 else comments[begin + 1 :]
    )
    reconstructed_lines = ["" if c is None else c for c in comments_in_range]
    if begin == 0:
        reconstructed_lines = _remove_empty_strings_from_begin(reconstructed_lines)
    if end == -1:
        reconstructed_lines = list(
            reversed(
                _remove_empty_strings_from_begin(list(reversed(reconstructed_lines)))
            )
        )
    return reconstructed_lines


def _remove_empty_strings_from_begin(lst: list) -> list:
    for i, el in enumerate(lst):
        if el != "":
            return lst[i:]
    return []


def _blank_lines_between(begin: int, end: int) -> int:
    return end - (begin + 1)
