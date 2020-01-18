import re
from typing import Callable, List, Optional, Set, Tuple

from lark import Tree, Token

from ..parser import parser
from .context import Context, ExpressionContext
from .enum import format_enum
from .expression import format_expression
from .constants import INDENT_SIZE, INLINE_COMMENT_OFFSET
from .types import Outcome, Node, FormattedLines


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
    formatted_lines, _ = _format_block(
        parse_tree.children, _format_class_statement, context
    )
    formatted_lines.append((None, ""))
    formatted_lines_with_inlined_comments = _add_inline_comments(
        formatted_lines, context.inline_comments
    )
    return "\n".join([line for _, line in formatted_lines_with_inlined_comments])


def _format_block(
    statements: List[Node], statement_formatter: Callable, context: Context,
) -> Outcome:
    formatted_lines = []  # type: List
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


def _format_class_statement(statement: Node, context: Context) -> Outcome:
    formatted_lines = []
    last_processed_line_no = statement.line
    if statement.data == "tool_stmt":
        formatted_lines.append((statement.line, "{}tool".format(context.indent_string)))
    elif statement.data == "class_def":
        name = statement.children[0].value
        formatted_lines.append(
            (statement.line, "{}class {}:".format(context.indent_string, name))
        )
        class_lines, last_processed_line_no = _format_block(
            statement.children[1:],
            _format_class_statement,
            context.create_child_context(last_processed_line_no),
        )
        formatted_lines += class_lines
    elif statement.data == "func_def":
        name = statement.children[0].value
        formatted_lines.append(
            (statement.line, "{}func {}():".format(context.indent_string, name))
        )
        func_lines, last_processed_line_no = _format_block(
            statement.children[1:],
            _format_func_statement,
            context.create_child_context(last_processed_line_no),
        )
        formatted_lines += func_lines
    elif statement.data == "enum_def":
        enum_lines, last_processed_line_no = format_enum(statement, context)
        formatted_lines += enum_lines
    return (formatted_lines, last_processed_line_no)


def _format_func_statement(statement: Node, context: Context) -> Outcome:
    formatted_lines = []
    last_processed_line_no = statement.line
    if statement.data == "pass_stmt":
        formatted_lines.append((statement.line, "{}pass".format(context.indent_string)))
    elif statement.data == "func_var_stmt":
        concrete_var_stmt = statement.children[0]
        if concrete_var_stmt.data == "var_assigned":
            name = concrete_var_stmt.children[0].value
            expr = concrete_var_stmt.children[1]
            expression_context = ExpressionContext(
                "var {} = ".format(name), statement.line, ""
            )
            lines, last_processed_line_no = format_expression(
                expr, expression_context, context
            )
            formatted_lines += lines
        elif concrete_var_stmt.data == "var_empty":
            name = concrete_var_stmt.children[0].value
            formatted_lines.append(
                (statement.line, "{}var {}".format(context.indent_string, name))
            )
    elif statement.data == "expr_stmt":
        expr = statement.children[0]
        expression_context = ExpressionContext("", statement.line, "")
        lines, last_processed_line_no = format_expression(
            expr, expression_context, context
        )
        formatted_lines += lines
    return (formatted_lines, last_processed_line_no)


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
        line_no += 1
    for line in context.gdscript_code_lines[line_no - 1 :: -1]:
        if line == "":  # TODO: all ws-lines (non-code&non-comment)
            line_no -= 1
        else:
            break
    return line_no


def _gather_standalone_comments_from_code(gdscript_code: str) -> List[Optional[str]]:
    return _gather_comments_from_code_by_regex(gdscript_code, r"\s*(#.*)$")


def _gather_inline_comments_from_code(gdscript_code: str) -> List[Optional[str]]:
    return _gather_comments_from_code_by_regex(gdscript_code, r"\s*[^\s#]+\s*(#.*)$")


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
