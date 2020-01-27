from typing import Dict, Callable
from functools import partial

from lark import Tree

from .types import Outcome, Node
from .context import Context, ExpressionContext
from .block import format_block
from .function_statement import format_func_statement
from .enum import format_enum
from .statement_utils import format_simple_statement
from .var_statement import format_var_statement
from .expression_to_str import expression_to_str
from .expression import format_comma_separated_list, format_expression


def format_class_statement(statement: Node, context: Context) -> Outcome:
    handlers = {
        "tool_stmt": partial(format_simple_statement, "tool"),
        "class_var_stmt": format_var_statement,
        "extends_stmt": _format_extends_statement,
        "class_def": _format_class_statement,
        "func_def": _format_func_statement,
        "enum_def": format_enum,
        "classname_stmt": _format_classname_statement,
        "signal_stmt": _format_signal_statement,
        "docstr_stmt": _format_docstring_statement,
        "const_stmt": _format_const_statement,
        "export_stmt": _format_export_statement,
        "onready_stmt": lambda s, c: format_var_statement(
            s.children[0], c, prefix="onready "
        ),
    }  # type: Dict[str, Callable]
    return handlers[statement.data](statement, context)


def _format_export_statement(statement: Tree, context: Context) -> Outcome:
    concrete_export_statement = statement.children[0]
    if concrete_export_statement.data == "export_inf":
        return format_var_statement(
            concrete_export_statement, context, prefix="export "
        )
    expression_context = ExpressionContext("export(", statement.line, ")")
    prefix_lines, _ = (
        format_comma_separated_list(
            concrete_export_statement.children[:-1], expression_context, context
        ),
        statement.end_line,
    )
    _, last_line = prefix_lines[-1]
    prefix = "{} ".format(last_line.strip())
    expr_lines, _ = format_var_statement(
        concrete_export_statement.children[-1], context, prefix=prefix
    )
    return (prefix_lines[:-1] + expr_lines, statement.end_line)


def _format_const_statement(statement: Tree, context: Context) -> Outcome:
    if len(statement.children) == 4:
        prefix = "const {} = ".format(statement.children[1].value)
    elif len(statement.children) == 5:
        prefix = "const {} := ".format(statement.children[1].value)
    elif len(statement.children) == 6:
        prefix = "const {}: {} = ".format(
            statement.children[1].value, statement.children[3].value
        )
    else:
        raise NotImplementedError
    expression_context = ExpressionContext(prefix, statement.line, "")
    return format_expression(statement.children[-1], expression_context, context)


def _format_docstring_statement(statement: Tree, context: Context) -> Outcome:
    expression_context = ExpressionContext("", statement.line, "")
    return format_expression(statement.children[0], expression_context, context)


def _format_signal_statement(statement: Node, context: Context) -> Outcome:
    if len(statement.children) == 1:
        return format_simple_statement(
            "signal {}".format(statement.children[0].value), statement, context
        )
    expression_context = ExpressionContext(
        "signal {}(".format(statement.children[0].value), statement.line, ")"
    )
    return (
        format_comma_separated_list(
            statement.children[1:], expression_context, context
        ),
        statement.end_line,
    )


def _format_classname_statement(statement: Node, context: Context) -> Outcome:
    last_processed_line_no = statement.line
    optional_string = (
        ""
        if len(statement.children) == 1
        else ", {}".format(expression_to_str(statement.children[1]))
    )
    formatted_lines = [
        (
            statement.line,
            "{}class_name {}{}".format(
                context.indent_string, statement.children[0].value, optional_string
            ),
        )
    ]
    return (formatted_lines, last_processed_line_no)


def _format_extends_statement(statement: Node, context: Context) -> Outcome:
    last_processed_line_no = statement.line
    optional_attributes = (
        ""
        if len(statement.children) == 1
        else ".{}".format(
            ".".join([expression_to_str(child) for child in statement.children[1:]])
        )
    )
    formatted_lines = [
        (
            statement.line,
            "{}extends {}{}".format(
                context.indent_string,
                expression_to_str(statement.children[0]),
                optional_attributes,
            ),
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
