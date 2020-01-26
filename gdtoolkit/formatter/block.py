import re
from typing import List, Callable

from .types import Outcome, Node, FormattedLines
from .context import Context
from .constants import INDENT_SIZE


def format_block(
    statements: List[Node], statement_formatter: Callable, context: Context,
) -> Outcome:
    print(len(statements))
    formatted_lines = []  # type: FormattedLines
    previously_processed_line_number = context.previously_processed_line_number
    for statement in statements:
        blank_lines = _reconstruct_blank_lines_in_range(
            previously_processed_line_number, statement.line, context,
        )
        if previously_processed_line_number == context.previously_processed_line_number:
            blank_lines = _remove_empty_strings_from_begin(blank_lines)
        formatted_lines += blank_lines
        lines, previously_processed_line_number = statement_formatter(
            statement, context
        )
        formatted_lines += lines
    dedent_line_number = _find_dedent_line_number(
        previously_processed_line_number, context
    )
    lines_at_the_end = _reconstruct_blank_lines_in_range(
        previously_processed_line_number, dedent_line_number, context,
    )
    lines_at_the_end = _remove_empty_strings_from_end(lines_at_the_end)
    formatted_lines += lines_at_the_end
    previously_processed_line_number = dedent_line_number - 1
    return (formatted_lines, previously_processed_line_number)


# TODO: indent detection & refactoring
def _find_dedent_line_number(
    previously_processed_line_number: int, context: Context
) -> int:
    if (
        previously_processed_line_number == len(context.gdscript_code_lines) - 1
        or context.indent == 0
    ):
        return len(context.gdscript_code_lines)
    line_no = previously_processed_line_number + 1
    for line in context.gdscript_code_lines[previously_processed_line_number + 1 :]:
        if (
            line.startswith(" ")
            and re.search(r"^ {0,%d}[^ ]+" % (context.indent - 1), line) is not None
        ):
            break
        if (
            line.startswith("\t")
            and re.search(
                r"^\t{0,%d}[^\t]+" % ((context.indent / INDENT_SIZE) - 1), line
            )
            is not None
        ):
            break
        if (
            context.indent > 0
            and len(line) > 0
            and not line.startswith(" ")
            and not line.startswith("\t")
        ):
            break
        line_no += 1
    for line in context.gdscript_code_lines[line_no - 1 :: -1]:
        if line == "":  # TODO: all ws-lines (non-code&non-comment)
            line_no -= 1
        else:
            break
    return line_no


def _reconstruct_blank_lines_in_range(
    begin: int, end: int, context: Context
) -> FormattedLines:
    prefix = context.indent_string
    comments_in_range = context.standalone_comments[begin + 1 : end]
    reconstructed_lines = ["" if c is None else prefix + c for c in comments_in_range]
    reconstructed_lines = _squeeze_lines(reconstructed_lines)
    return list(zip([None for _ in range(begin + 1, end)], reconstructed_lines))


def _squeeze_lines(lines: List[str]) -> List[str]:
    squeezed_lines = []
    previous_line = None
    for line in lines:
        if line != "" or previous_line != "":
            squeezed_lines.append(line)
        previous_line = line
    return squeezed_lines


def _remove_empty_strings_from_begin(lst: FormattedLines) -> FormattedLines:
    for i, (_, line) in enumerate(lst):
        if line != "":
            return lst[i:]
    return []


def _remove_empty_strings_from_end(lst: FormattedLines) -> FormattedLines:
    return list(reversed(_remove_empty_strings_from_begin(list(reversed(lst)))))
