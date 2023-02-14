from functools import partial
from typing import Dict, Callable, Optional

from lark import Tree

from ..common.utils import get_line
from .context import Context, ExpressionContext
from .types import Outcome, FormattedLines
from .expression import format_expression
from .block import format_block, reconstruct_blank_lines_in_range
from .statement_utils import format_simple_statement
from .var_statement import format_var_statement
from .const_statement import format_const_statement


def format_func_statement(statement: Tree, context: Context) -> Outcome:
    handlers = {
        "pass_stmt": partial(format_simple_statement, "pass"),
        "func_var_stmt": format_var_statement,
        "const_stmt": format_const_statement,
        "expr_stmt": _format_expr_statement,
        "return_stmt": _format_return_statement,
        "break_stmt": partial(format_simple_statement, "break"),
        "continue_stmt": partial(format_simple_statement, "continue"),
        "if_stmt": _format_if_statement,
        "while_stmt": partial(_format_branch, "while ", ":", 0),
        "for_stmt": _format_for_statement,
        "match_stmt": _format_match_statement,
        # fake statements:
        "match_branch": _format_match_branch,
    }  # type: Dict[str, Callable]
    return handlers[statement.data](statement, context)


def _format_expr_statement(statement: Tree, context: Context) -> Outcome:
    expr = statement.children[0]
    expression_context = ExpressionContext(
        "", get_line(statement), "", get_line(statement)
    )
    return format_expression(expr, expression_context, context)


def _format_return_statement(statement: Tree, context: Context) -> Outcome:
    if len(statement.children) == 0:
        return format_simple_statement("return", statement, context)
    expr = statement.children[0]
    expression_context = ExpressionContext(
        "return ", get_line(statement), "", get_line(statement)
    )
    return format_expression(expr, expression_context, context)


def _format_if_statement(statement: Tree, context: Context) -> Outcome:
    formatted_lines = []  # type: FormattedLines
    previously_processed_line_number = None
    for branch in statement.children:
        if previously_processed_line_number is not None:
            blank_lines = reconstruct_blank_lines_in_range(
                previously_processed_line_number, get_line(branch), context
            )
            formatted_lines += blank_lines
        branch_prefix = {
            "if_branch": "if ",
            "elif_branch": "elif ",
            "else_branch": "else",
        }[branch.data]
        expr_position = {"if_branch": 0, "elif_branch": 0, "else_branch": None}[
            branch.data
        ]
        lines, previously_processed_line_number = _format_branch(
            branch_prefix, ":", expr_position, branch, context
        )
        formatted_lines += lines
    return (formatted_lines, previously_processed_line_number)  # type: ignore


def _format_for_statement(statement: Tree, context: Context) -> Outcome:
    prefix = f"for {statement.children[0].value} in "
    suffix = ":"
    expr_position = 1
    return _format_branch(prefix, suffix, expr_position, statement, context)


def _format_match_statement(statement: Tree, context: Context) -> Outcome:
    prefix = "match "
    suffix = ":"
    expr_position = 0
    return _format_branch(prefix, suffix, expr_position, statement, context)


def _format_match_branch(statement: Tree, context: Context) -> Outcome:
    prefix = ""
    suffix = ":"
    expr_position = 0
    return _format_branch(prefix, suffix, expr_position, statement, context)


def _format_branch(
    prefix: str,
    suffix: str,
    expr_position: Optional[int],
    statement: Tree,
    context: Context,
) -> Outcome:
    if expr_position is not None:
        expr = statement.children[expr_position]
        expression_context = ExpressionContext(
            prefix, get_line(statement), suffix, get_line(statement)
        )
        header_lines, last_processed_line_no = format_expression(
            expr, expression_context, context
        )
        offset = expr_position + 1
    else:
        header_lines = [
            (
                get_line(statement),
                "{}{}{}".format(context.indent_string, prefix, suffix),
            )
        ]
        last_processed_line_no = get_line(statement)
        offset = 0
    body_lines, last_processed_line_no = format_block(
        statement.children[offset:],
        format_func_statement,
        context.create_child_context(last_processed_line_no),
    )
    return (header_lines + body_lines, last_processed_line_no)
