from typing import Dict, Callable

from .context import Context, ExpressionContext
from .types import Outcome, Node
from .expression import format_expression
from .statement_utils import format_simple_statement


def format_var_statement(
    statement: Node, context: Context, prefix: str = ""
) -> Outcome:
    concrete_var_stmt = statement.children[0]
    handlers = {
        "var_empty": _format_var_empty_statement,
        "var_assigned": _format_var_assigned_statement,
        "var_typed": _format_var_typed_statement,
        "var_typed_assgnd": _format_var_typed_assigned_statement,
        "var_inf": _format_var_inferred_statement,
    }  # type: Dict[str, Callable]
    return handlers[concrete_var_stmt.data](concrete_var_stmt, context, prefix)


def _format_var_empty_statement(
    statement: Node, context: Context, prefix: str = ""
) -> Outcome:
    return format_simple_statement(
        "{}var {}".format(prefix, statement.children[0].value), statement, context
    )


def _format_var_typed_statement(
    statement: Node, context: Context, prefix: str = ""
) -> Outcome:
    return format_simple_statement(
        "{}var {}: {}".format(
            prefix, statement.children[0].value, statement.children[1].value
        ),
        statement,
        context,
    )


def _format_var_assigned_statement(
    statement: Node, context: Context, prefix: str = ""
) -> Outcome:
    name = statement.children[0].value
    expr = statement.children[1]
    expression_context = ExpressionContext(
        "{}var {} = ".format(prefix, name), statement.line, "", statement.end_line
    )
    return format_expression(expr, expression_context, context)


def _format_var_inferred_statement(
    statement: Node, context: Context, prefix: str = ""
) -> Outcome:
    name = statement.children[0].value
    expr = statement.children[1]
    expression_context = ExpressionContext(
        "{}var {} := ".format(prefix, name), statement.line, "", statement.end_line
    )
    return format_expression(expr, expression_context, context)


def _format_var_typed_assigned_statement(
    statement: Node, context: Context, prefix: str = ""
) -> Outcome:
    var_name = statement.children[0].value
    type_name = statement.children[1].value
    expr = statement.children[2]
    expression_context = ExpressionContext(
        "{}var {}: {} = ".format(prefix, var_name, type_name),
        statement.line,
        "",
        statement.end_line,
    )
    return format_expression(expr, expression_context, context)
