from typing import Dict, Callable
from functools import partial

from lark import Tree

from ..common.utils import get_line, get_end_line
from .types import FormattedLines, Outcome
from .context import Context, ExpressionContext
from .block import format_block
from .function_statement import format_func_statement
from .statement_utils import format_simple_statement
from .var_statement import format_var_statement
from .expression_to_str import expression_to_str
from .expression import format_concrete_expression
from .annotation import format_standalone_annotation
from .property import (
    has_inline_property_body,
    append_property_body_to_formatted_line,
    format_property_body,
)
from .const_statement import format_const_statement


def format_class_statement(statement: Tree, context: Context) -> Outcome:
    handlers = {
        "pass_stmt": partial(format_simple_statement, "pass"),
        "enum_stmt": _format_enum_statement,
        "signal_stmt": _format_signal_statement,
        "extends_stmt": _format_extends_statement,
        "classname_stmt": _format_classname_statement,
        "classname_extends_stmt": _format_classname_extends_statement,
        "class_var_stmt": _format_var_statement,
        "static_class_var_stmt": lambda s, c: _format_var_statement(
            s.children[0], c, "static "
        ),
        "const_stmt": format_const_statement,
        "docstr_stmt": _format_docstring_statement,
        "class_def": _format_class_statement,
        "func_def": _format_func_statement,
        "static_func_def": lambda s, c: _format_func_statement(
            s.children[0], c, "static "
        ),
        "annotation": format_standalone_annotation,
        "property_body_def": format_property_body,
    }  # type: Dict[str, Callable]
    return handlers[statement.data](statement, context)


def _format_signal_statement(statement: Tree, context: Context) -> Outcome:
    if len(statement.children) == 1 or len(statement.children[1].children) == 0:
        return format_simple_statement(
            f"signal {statement.children[0].value}", statement, context
        )
    expression_context = ExpressionContext(
        f"signal {statement.children[0].value}",
        get_line(statement),
        "",
        get_end_line(statement),
    )
    signal_args = statement.children[-1]
    return format_concrete_expression(signal_args, expression_context, context)


def _format_classname_statement(statement: Tree, context: Context) -> Outcome:
    last_processed_line_no = get_line(statement)
    formatted_lines: FormattedLines = [
        (
            get_line(statement),
            f"{context.indent_string}class_name {statement.children[0].value}",
        )
    ]
    return (formatted_lines, last_processed_line_no)


def _format_extends_statement(statement: Tree, context: Context) -> Outcome:
    last_processed_line_no = get_line(statement)
    optional_attributes = (
        ""
        if len(statement.children) == 1
        else ".{}".format(
            ".".join([expression_to_str(child) for child in statement.children[1:]])
        )
    )
    formatted_lines: FormattedLines = [
        (
            get_line(statement),
            "{}extends {}{}".format(
                context.indent_string,
                expression_to_str(statement.children[0]),
                optional_attributes,
            ),
        )
    ]
    return (formatted_lines, last_processed_line_no)


def _format_classname_extends_statement(statement: Tree, context: Context) -> Outcome:
    last_processed_line_no = get_line(statement)
    extendee_pos = 2 + 1
    optional_attributes = (
        ""
        if len(statement.children) <= extendee_pos + 1
        else ".{}".format(
            ".".join(
                [
                    expression_to_str(child)
                    for child in statement.children[extendee_pos + 1 :]
                ]
            )
        )
    )
    formatted_lines: FormattedLines = [
        (
            get_line(statement),
            "{}class_name {} extends {}{}".format(
                context.indent_string,
                statement.children[1].value,
                expression_to_str(statement.children[extendee_pos]),
                optional_attributes,
            ),
        )
    ]
    return (formatted_lines, last_processed_line_no)


def _format_var_statement(
    statement: Tree, context: Context, prefix: str = ""
) -> Outcome:
    formatted_lines, last_processed_line = format_var_statement(
        statement, context, prefix
    )
    concrete_var_statement = statement.children[0]
    if has_inline_property_body(concrete_var_statement):
        inline_property_body = concrete_var_statement.children[-1]
        formatted_lines = formatted_lines[:-1] + append_property_body_to_formatted_line(
            formatted_lines[-1], inline_property_body, context
        )
    return formatted_lines, last_processed_line


def _format_docstring_statement(statement: Tree, context: Context) -> Outcome:
    expression_context = ExpressionContext(
        "", get_line(statement), "", get_end_line(statement)
    )
    return format_concrete_expression(
        statement.children[0], expression_context, context
    )


def _format_class_statement(statement: Tree, context: Context) -> Outcome:
    last_processed_line_no = get_line(statement)
    name = statement.children[0].value
    formatted_lines: FormattedLines = [
        (get_line(statement), f"{context.indent_string}class {name}:")
    ]
    class_lines, last_processed_line_no = format_block(
        statement.children[1:],
        format_class_statement,
        context.create_child_context(last_processed_line_no),
    )
    formatted_lines += class_lines
    return (formatted_lines, last_processed_line_no)


def _format_func_statement(
    statement: Tree, context: Context, prefix: str = ""
) -> Outcome:
    func_header = statement.children[0]
    formatted_lines, last_processed_line_no = _format_func_header(
        func_header, context, prefix
    )
    func_lines, last_processed_line_no = format_block(
        statement.children[1:],
        format_func_statement,
        context.create_child_context(last_processed_line_no),
    )
    formatted_lines += func_lines
    return (formatted_lines, last_processed_line_no)


def _format_func_header(statement: Tree, context: Context, prefix: str) -> Outcome:
    name = statement.children[0].value
    has_return_type = len(statement.children) > 2
    expression_context = ExpressionContext(
        f"{prefix}func {name}",
        get_line(statement),
        f" -> {statement.children[2].value}:" if has_return_type else ":",
        get_end_line(statement),
    )
    func_args = statement.children[1]
    return format_concrete_expression(func_args, expression_context, context)


def _format_enum_statement(statement: Tree, context: Context) -> Outcome:
    actual_enum = statement.children[0]
    prefix = (
        f"enum {actual_enum.children[0].value} "
        if len(actual_enum.children) == 2
        else "enum "
    )
    expression_context = ExpressionContext(
        prefix, get_line(statement), "", get_end_line(statement)
    )
    enum_body = actual_enum.children[-1]
    return format_concrete_expression(enum_body, expression_context, context)
