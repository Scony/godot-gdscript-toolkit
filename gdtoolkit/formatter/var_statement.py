from typing import Dict, Callable

from lark import Tree

from .context import Context, ExpressionContext
from .types import Outcome, Node
from .expression import format_expression
from .expression_utils import is_any_comma
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
    outcome = handlers[concrete_var_stmt.data](concrete_var_stmt, context, prefix)
    setget = (
        statement.children[1]
        if len(statement.children) > 1 and statement.children[1].data == "setget"
        else None
    )
    if setget is None:
        return outcome
    return _format_setget_and_append_to_outcome(setget, outcome)


def _format_setget_and_append_to_outcome(setget: Tree, outcome: Outcome) -> Outcome:
    setget_string = (
        " setget {}, {}".format(setget.children[1].value, setget.children[3].value)
        if len(setget.children) > 2 and is_any_comma(setget.children[2])
        else (
            " setget {}".format(setget.children[1])
            if len(setget.children) == 2
            else " setget , {}".format(setget.children[2].value)
        )
    )
    formatted_lines, _ = outcome
    last_line_no, last_line = formatted_lines[-1]
    formatted_lines = formatted_lines[:-1] + [(last_line_no, last_line + setget_string)]
    return (formatted_lines, setget.end_line)


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
        "{}var {} = ".format(prefix, name), statement.line, ""
    )
    return format_expression(expr, expression_context, context)


def _format_var_inferred_statement(
    statement: Node, context: Context, prefix: str = ""
) -> Outcome:
    name = statement.children[0].value
    expr = statement.children[1]
    expression_context = ExpressionContext(
        "{}var {} := ".format(prefix, name), statement.line, ""
    )
    return format_expression(expr, expression_context, context)


def _format_var_typed_assigned_statement(
    statement: Node, context: Context, prefix: str = ""
) -> Outcome:
    var_name = statement.children[0].value
    type_name = statement.children[1].value
    expr = statement.children[2]
    expression_context = ExpressionContext(
        "{}var {}: {} = ".format(prefix, var_name, type_name), statement.line, ""
    )
    return format_expression(expr, expression_context, context)
