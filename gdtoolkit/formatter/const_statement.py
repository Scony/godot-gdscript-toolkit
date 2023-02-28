from lark import Tree

from ..common.utils import get_line, get_end_line
from .types import Outcome
from .context import Context, ExpressionContext
from .expression import format_expression


def format_const_statement(statement: Tree, context: Context) -> Outcome:
    concrete_const_stmt = statement.children[0]
    handlers = {
        "const_assigned": _format_const_assigned_statement,
        "const_typed_assigned": _format_const_typed_assigned_statement,
        "const_inf": _format_const_inferred_statement,
    }
    return handlers[concrete_const_stmt.data](concrete_const_stmt, context)


def _format_const_assigned_statement(statement: Tree, context: Context) -> Outcome:
    expression_context = ExpressionContext(
        f"const {statement.children[0].value} = ",
        get_line(statement),
        "",
        get_end_line(statement),
    )
    return format_expression(statement.children[-1], expression_context, context)


def _format_const_typed_assigned_statement(
    statement: Tree, context: Context
) -> Outcome:
    expression_context = ExpressionContext(
        f"const {statement.children[0].value}: {statement.children[1].value} = ",
        get_line(statement),
        "",
        get_end_line(statement),
    )
    return format_expression(statement.children[-1], expression_context, context)


def _format_const_inferred_statement(statement: Tree, context: Context) -> Outcome:
    expression_context = ExpressionContext(
        f"const {statement.children[0].value} := ",
        get_line(statement),
        "",
        get_end_line(statement),
    )
    return format_expression(statement.children[-1], expression_context, context)
