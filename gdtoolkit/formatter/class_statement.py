from typing import Dict, Callable
from functools import partial

from lark import Tree, Token

from .types import Outcome, Node
from .context import Context, ExpressionContext
from .block import format_block
from .function_statement import format_func_statement
from .enum import format_enum
from .statement_utils import (
    format_simple_statement,
    find_tree_among_children,
    find_token_among_children,
)
from .var_statement import format_var_statement
from .expression_to_str import expression_to_str
from .expression import format_comma_separated_list, format_expression
from .expression_utils import is_any_comma


def format_class_statement(statement: Node, context: Context) -> Outcome:
    handlers = {
        "tool_stmt": partial(format_simple_statement, "tool"),
        "pass_stmt": partial(format_simple_statement, "pass"),
        "class_var_stmt": format_var_statement,
        "extends_stmt": _format_extends_statement,
        "class_def": _format_class_statement,
        "func_def": _format_func_statement,
        "enum_def": format_enum,
        "classname_stmt": _format_classname_statement,
        "classname_extends_stmt": _format_classname_extends_statement,
        "signal_stmt": _format_signal_statement,
        "docstr_stmt": _format_docstring_statement,
        "const_stmt": _format_const_statement,
        "export_stmt": _format_export_statement,
        "onready_stmt": lambda s, c: format_var_statement(
            s.children[0], c, prefix="onready "
        ),
        "puppet_var_stmt": lambda s, c: format_var_statement(
            s.children[0], c, prefix="puppet "
        ),
        "static_func_def": partial(
            _format_child_and_prepend_to_outcome, prefix="static "
        ),
        "remote_func_def": partial(
            _format_child_and_prepend_to_outcome, prefix="remote "
        ),
        "remotesync_func_def": partial(
            _format_child_and_prepend_to_outcome, prefix="remotesync "
        ),
        "master_func_def": partial(
            _format_child_and_prepend_to_outcome, prefix="master "
        ),
        "mastersync_func_def": partial(
            _format_child_and_prepend_to_outcome, prefix="mastersync "
        ),
        "puppet_func_def": partial(
            _format_child_and_prepend_to_outcome, prefix="puppet "
        ),
        "puppetsync_func_def": partial(
            _format_child_and_prepend_to_outcome, prefix="puppetsync "
        ),
        "sync_func_def": partial(_format_child_and_prepend_to_outcome, prefix="sync "),
    }  # type: Dict[str, Callable]
    return handlers[statement.data](statement, context)


def _format_child_and_prepend_to_outcome(
    statement: Node, context: Context, prefix: str
) -> Outcome:
    lines, last_processed_line = format_class_statement(statement.children[0], context)
    first_line_no, first_line = lines[0]
    return (
        [
            (
                first_line_no,
                "{}{}{}".format(context.indent_string, prefix, first_line.strip()),
            )
        ]
        + lines[1:],
        last_processed_line,
    )


def _format_export_statement(statement: Tree, context: Context) -> Outcome:
    concrete_export_statement = statement.children[0]
    addons = [
        child.data
        for child in concrete_export_statement.children
        if isinstance(child, Tree) and child.data in ["puppet", "onready"]
    ]
    addon_present = len(addons) > 0
    if concrete_export_statement.data == "export_inf":
        addon = "{} ".format(addons[0]) if addon_present else ""
        var_statement = (
            Tree("fake_var_stmt", concrete_export_statement.children[1:])
            if addon_present
            else concrete_export_statement
        )
        return format_var_statement(
            var_statement, context, prefix="export {}".format(addon)
        )
    addon = " {}".format(addons[0]) if addon_present else ""
    expression_context = ExpressionContext(
        "export(",
        statement.line,
        "){}".format(addon),
        concrete_export_statement.children[-1].line,
    )
    export_hints = (
        concrete_export_statement.children[:-2]
        if addon_present
        else concrete_export_statement.children[:-1]
    )
    prefix_lines, _ = (
        format_comma_separated_list(export_hints, expression_context, context),
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
    expression_context = ExpressionContext(
        prefix, statement.line, "", statement.end_line
    )
    return format_expression(statement.children[-1], expression_context, context)


def _format_docstring_statement(statement: Tree, context: Context) -> Outcome:
    expression_context = ExpressionContext("", statement.line, "", statement.end_line)
    return format_expression(statement.children[0], expression_context, context)


def _format_signal_statement(statement: Node, context: Context) -> Outcome:
    if len(statement.children) == 1:
        return format_simple_statement(
            "signal {}".format(statement.children[0].value), statement, context
        )
    expression_context = ExpressionContext(
        "signal {}(".format(statement.children[0].value),
        statement.line,
        ")",
        statement.end_line,
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


def _format_classname_extends_statement(statement: Node, context: Context) -> Outcome:
    last_processed_line_no = statement.line
    optional_string = (
        ""
        if isinstance(statement.children[2], Token)
        and statement.children[2].value == "extends"
        else ", {}".format(expression_to_str(statement.children[3]))
    )
    extendee_pos = (
        2 + 1
        if isinstance(statement.children[2], Token)
        and statement.children[2].value == "extends"
        else 4 + 1
    )
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
    formatted_lines = [
        (
            statement.line,
            "{}class_name {}{} extends {}{}".format(
                context.indent_string,
                statement.children[1].value,
                optional_string,
                expression_to_str(statement.children[extendee_pos]),
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


def _format_func_statement(statement: Tree, context: Context) -> Outcome:
    func_header = statement.children[0]
    formatted_lines, last_processed_line_no = _format_func_header(func_header, context)
    func_lines, last_processed_line_no = format_block(
        statement.children[1:],
        format_func_statement,
        context.create_child_context(last_processed_line_no),
    )
    formatted_lines += func_lines
    return (formatted_lines, last_processed_line_no)


def _format_func_header(statement: Tree, context: Context) -> Outcome:
    return_type = find_token_among_children("TYPE", statement)
    suffix_w_parent = ":" if return_type is None else f" -> {return_type.value}:"
    parent_call = find_tree_among_children("parent_call", statement)
    suffix_wo_parent = suffix_w_parent if parent_call is None else ""
    name_token = statement.children[0]
    name = name_token.value
    func_args = find_tree_among_children("func_args", statement)
    if func_args is not None:
        expression_context = ExpressionContext(
            f"func {name}(",
            statement.line,
            f"){suffix_wo_parent}",
            func_args.end_line,
        )
        formatted_lines = format_comma_separated_list(
            func_args.children, expression_context, context
        )
    else:
        formatted_lines = [
            (
                name_token.line,
                f"{context.indent_string}func {name}(){suffix_wo_parent}",
            )
        ]
    if parent_call is not None:
        last_line_no, last_line = formatted_lines[-1]
        expression_context = ExpressionContext(
            f"{last_line.strip()}.(",
            last_line_no,  # type: ignore
            f"){suffix_w_parent}",
            parent_call.end_line,
        )
        elements = [e for e in parent_call.children[1:-1] if not is_any_comma(e)]
        formatted_lines = formatted_lines[:-1] + format_comma_separated_list(
            elements, expression_context, context
        )
    return (formatted_lines, statement.end_line)
