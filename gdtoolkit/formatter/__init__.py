from .formatter import format_code  # noqa: F401
from .safety_checks import (
    check_tree_invariant,
    check_formatting_stability,
    check_comment_persistence,
)


def check_formatting_safety(
    given_code: str, formatted_code: str, max_line_length: int
) -> None:
    if given_code == formatted_code:
        return
    check_comment_persistence(given_code, formatted_code)
    check_tree_invariant(given_code, formatted_code)
    check_formatting_stability(formatted_code, max_line_length)
