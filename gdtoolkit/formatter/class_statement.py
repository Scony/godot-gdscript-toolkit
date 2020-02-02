from typing import Dict, Callable
from functools import partial

from lark import Tree, Token

from .types import Outcome, Node
from .context import Context, ExpressionContext
from .block import format_block
from .function_statement import format_func_statement
from .enum import format_enum
from .statement_utils import format_simple_statement
from .var_statement import format_var_statement
from .expression_to_str import expression_to_str
from .expression import format_comma_separated_list, format_expression
from .expression_utils import is_any_comma


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
        "puppet_func_def": partial(
            _format_child_and_prepend_to_outcome, prefix="puppet "
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
    if concrete_export_statement.data == "export_inf":
        return format_var_statement(
            concrete_export_statement, context, prefix="export "
        )
    expression_context = ExpressionContext("export (", statement.line, ")")
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


def _format_func_statement(statement: Tree, context: Context) -> Outcome:
    def _has_func_args(statement):
        return (
            len(statement.children) > 1
            and isinstance(statement.children[1], Tree)
            and statement.children[1].data == "func_args"
        )

    def _has_parent_call(statement):
        return (
            len(statement.children) > 1
            and isinstance(statement.children[1], Tree)
            and statement.children[1].data == "parent_call"
        ) or (
            len(statement.children) > 2
            and isinstance(statement.children[2], Tree)
            and statement.children[2].data == "parent_call"
        )

    def _has_return_type(statement):
        return any(
            isinstance(c, Token) and c.type == "TYPE"
            for c in statement.children[1 : (3 + 1)]
        )

    first_statement_offset = 1
    first_statement_offset = (
        first_statement_offset + 1
        if _has_func_args(statement)
        else first_statement_offset
    )
    first_statement_offset = (
        first_statement_offset + 1
        if _has_parent_call(statement)
        else first_statement_offset
    )
    first_statement_offset = (
        first_statement_offset + 1
        if _has_return_type(statement)
        else first_statement_offset
    )
    formatted_lines, last_processed_line_no = _format_func_header(statement, context)
    func_lines, last_processed_line_no = format_block(
        statement.children[first_statement_offset:],
        format_func_statement,
        context.create_child_context(last_processed_line_no),
    )
    formatted_lines += func_lines
    return (formatted_lines, last_processed_line_no)


# TODO: refactor that beast ^^
def _format_func_header(statement: Tree, context: Context) -> Outcome:
    name_token = statement.children[0]
    name = name_token.value
    func_args = (
        statement.children[1]
        if isinstance(statement.children[1], Tree)
        and statement.children[1].data == "func_args"
        else None
    )
    if func_args is not None:
        expression_context = ExpressionContext(
            "func {}(".format(name), statement.line, ")"
        )
        formatted_lines = format_comma_separated_list(
            func_args.children, expression_context, context
        )
    else:
        formatted_lines = [
            (name_token.line, "{}func {}()".format(context.indent_string, name))
        ]
    parent_call = (
        statement.children[1]
        if isinstance(statement.children[1], Tree)
        and statement.children[1].data == "parent_call"
        else None
    )
    parent_call = (
        statement.children[2]
        if len(statement.children) > 2
        and isinstance(statement.children[2], Tree)
        and statement.children[2].data == "parent_call"
        else parent_call
    )
    if parent_call is not None:
        last_line_no, last_line = formatted_lines[-1]
        expression_context = ExpressionContext(
            "{}.(".format(last_line.strip()), last_line_no, ")"  # type: ignore
        )
        elements = [e for e in parent_call.children[1:-1] if not is_any_comma(e)]
        formatted_lines = formatted_lines[:-1] + format_comma_separated_list(
            elements, expression_context, context
        )
    return_type = (
        statement.children[1]
        if isinstance(statement.children[1], Token)
        and statement.children[1].type == "TYPE"
        else None
    )
    return_type = (
        statement.children[2]
        if len(statement.children) > 2
        and isinstance(statement.children[2], Token)
        and statement.children[2].type == "TYPE"
        else return_type
    )
    return_type = (
        statement.children[3]
        if len(statement.children) > 3
        and isinstance(statement.children[3], Token)
        and statement.children[3].type == "TYPE"
        else return_type
    )
    if return_type is not None:
        last_line_no, last_line = formatted_lines[-1]
        expression_context = ExpressionContext(
            "{} -> ".format(last_line.strip()), last_line_no, ":"  # type: ignore
        )
        formatted_lines = formatted_lines[:-1] + [
            (
                last_line_no,
                "{}{} -> {}:".format(
                    context.indent_string, last_line.strip(), return_type.value
                ),
            )
        ]
    else:
        last_line_no, last_line = formatted_lines[-1]  # type: ignore
        formatted_lines = formatted_lines[:-1] + [
            (last_line_no, "{}:".format(last_line))
        ]
    return (
        formatted_lines,
        statement.line,
    )
