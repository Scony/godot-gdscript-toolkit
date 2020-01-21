from functools import partial
from typing import Dict, Callable

from .context import Context, ExpressionContext
from .types import Outcome, Node, FormattedLines
from .expression import format_expression


def format_func_statement(statement: Node, context: Context) -> Outcome:
    handlers = {
        "pass_stmt": partial(_format_simple_statement, "pass"),
        "func_var_stmt": _format_func_var_statement,
        "expr_stmt": _format_expr_statement,
        "return_stmt": _format_return_statement,
        "break_stmt": partial(_format_simple_statement, "break"),
        "continue_stmt": partial(_format_simple_statement, "continue"),
    }  # type: Dict[str, Callable]
    return handlers[statement.data](statement, context)


def _format_func_var_statement(statement: Node, context: Context) -> Outcome:
    formatted_lines = []  # type: FormattedLines
    last_processed_line_no = statement.line
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
    return (formatted_lines, last_processed_line_no)


def _format_expr_statement(statement: Node, context: Context) -> Outcome:
    expr = statement.children[0]
    expression_context = ExpressionContext("", statement.line, "")
    return format_expression(expr, expression_context, context)


def _format_return_statement(statement: Node, context: Context) -> Outcome:
    if len(statement.children) == 0:
        return _format_simple_statement("return", statement, context)
    expr = statement.children[0]
    expression_context = ExpressionContext("return ", statement.line, "")
    return format_expression(expr, expression_context, context)


def _format_simple_statement(
    statement_name: str, statement: Node, context: Context
) -> Outcome:
    return (
        [(statement.line, "{}{}".format(context.indent_string, statement_name))],
        statement.line,
    )
