from typing import Dict, Callable
from functools import partial

from .types import Outcome, Node
from .context import Context
from .block import format_block
from .function_statement import format_func_statement
from .enum import format_enum
from .statement_utils import format_simple_statement
from .var_statement import format_var_statement


def format_class_statement(statement: Node, context: Context) -> Outcome:
    handlers = {
        "tool_stmt": partial(format_simple_statement, "tool"),
        "class_var_stmt": format_var_statement,
        "extends_stmt": _format_extends_statement,
        "class_def": _format_class_statement,
        "func_def": _format_func_statement,
        "enum_def": format_enum,
    }  # type: Dict[str, Callable]
    return handlers[statement.data](statement, context)


def _format_extends_statement(statement: Node, context: Context) -> Outcome:
    last_processed_line_no = statement.line
    formatted_lines = [
        (
            statement.line,
            "{}extends {}".format(context.indent_string, statement.children[0].value),
        )
    ]
    return (formatted_lines, last_processed_line_no)


def _format_class_statement(statement: Node, context: Context) -> Outcome:
    last_processed_line_no = statement.line
    name = statement.children[0].value
    formatted_lines = [
        (statement.line, "{}class {}:".format(context.indent_string, name))
    ]
    class_lines, last_processed_line_no = format_block(
        statement.children[1:],
        format_class_statement,
        context.create_child_context(last_processed_line_no),
    )
    formatted_lines += class_lines
    return (formatted_lines, last_processed_line_no)


def _format_func_statement(statement: Node, context: Context) -> Outcome:
    last_processed_line_no = statement.line
    name = statement.children[0].value
    formatted_lines = [
        (statement.line, "{}func {}():".format(context.indent_string, name))
    ]
    func_lines, last_processed_line_no = format_block(
        statement.children[1:],
        format_func_statement,
        context.create_child_context(last_processed_line_no),
    )
    formatted_lines += func_lines
    return (formatted_lines, last_processed_line_no)
