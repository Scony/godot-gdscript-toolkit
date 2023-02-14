from typing import Dict, Callable

from lark import Tree

from ..common.utils import get_line, get_end_line
from .context import Context, ExpressionContext
from .types import Outcome
from .expression import format_expression
from .statement_utils import format_simple_statement


def format_var_statement(
    statement: Tree, context: Context, prefix: str = ""
) -> Outcome:
    concrete_var_stmt = statement.children[0]
    handlers = {
        "class_var_empty": _format_var_empty_statement,
        "class_var_assigned": _format_var_assigned_statement,
        "class_var_typed": _format_var_typed_statement,
        "class_var_typed_assgnd": _format_var_typed_assigned_statement,
        "class_var_inf": _format_var_inferred_statement,
        "func_var_empty": _format_var_empty_statement,
        "func_var_assigned": _format_var_assigned_statement,
        "func_var_typed": _format_var_typed_statement,
        "func_var_typed_assgnd": _format_var_typed_assigned_statement,
        "func_var_inf": _format_var_inferred_statement,
    }  # type: Dict[str, Callable]
    return handlers[concrete_var_stmt.data](concrete_var_stmt, context, prefix)


def _format_var_empty_statement(
    statement: Tree, context: Context, prefix: str = ""
) -> Outcome:
    return format_simple_statement(
        "{}var {}".format(prefix, statement.children[0].value), statement, context
    )


def _format_var_typed_statement(
    statement: Tree, context: Context, prefix: str = ""
) -> Outcome:
    return format_simple_statement(
        "{}var {}: {}".format(
            prefix, statement.children[0].value, statement.children[1].value
        ),
        statement,
        context,
    )


def _format_var_assigned_statement(
    statement: Tree, context: Context, prefix: str = ""
) -> Outcome:
    name = statement.children[0].value
    expr = statement.children[1]
    expression_context = ExpressionContext(
        "{}var {} = ".format(prefix, name),
        get_line(statement),
        "",
        get_end_line(statement),
    )
    return format_expression(expr, expression_context, context)


def _format_var_inferred_statement(
    statement: Tree, context: Context, prefix: str = ""
) -> Outcome:
    name = statement.children[0].value
    expr = statement.children[1]
    expression_context = ExpressionContext(
        "{}var {} := ".format(prefix, name),
        get_line(statement),
        "",
        get_end_line(statement),
    )
    return format_expression(expr, expression_context, context)


def _format_var_typed_assigned_statement(
    statement: Tree, context: Context, prefix: str = ""
) -> Outcome:
    var_name = statement.children[0].value
    type_name = statement.children[1].value
    expr = statement.children[2]
    expression_context = ExpressionContext(
        "{}var {}: {} = ".format(prefix, var_name, type_name),
        get_line(statement),
        "",
        get_end_line(statement),
    )
    return format_expression(expr, expression_context, context)
