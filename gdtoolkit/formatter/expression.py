from functools import partial
from typing import Dict, Callable, List

from lark import Tree
from lark.tree import Meta

from .context import Context, ExpressionContext
from .types import Node, Outcome, FormattedLines
from .expression_utils import (
    remove_outer_parentheses,
    is_foldable,
    is_expression_forcing_multiple_lines,
    is_any_comma,
    is_trailing_comma,
    has_leading_dot,
)
from .expression_to_str import expression_to_str, standalone_expression_to_str


def format_expression(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    concrete_expression = expression.children[0]
    return (
        _format_standalone_expression(concrete_expression, expression_context, context)[
            0
        ],  # TODO: make those to not return last processed line (at the very end)
        expression.end_line,
    )


# TOOD: refactor
# pylint: disable=too-many-locals
def format_comma_separated_list(
    a_list: List[Node], expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    elements = [node for node in a_list if not is_any_comma(node)]
    child_context = context.create_child_context(expression_context.prefix_line)
    fake_meta = Meta()
    fake_meta.line = expression_context.prefix_line
    fake_meta.end_line = expression_context.suffix_line
    fake_expression = Tree("fake", a_list, fake_meta)
    multiline_mode_forced = is_expression_forcing_multiple_lines(
        fake_expression, context.standalone_comments
    )
    if not multiline_mode_forced or "preload" in expression_context.prefix_string:
        strings_to_join = list(map(standalone_expression_to_str, elements))
        single_line_expression = "{}{}{}".format(
            expression_context.prefix_string,
            ", ".join(strings_to_join),
            expression_context.suffix_string,
        )
        single_line_length = len(single_line_expression) + context.indent
        if (
            single_line_length <= context.max_line_length
            or "preload" in expression_context.prefix_string
        ):
            return [
                (
                    expression_context.prefix_line,
                    "{}{}".format(context.indent_string, single_line_expression),
                )
            ]
        indented_single_line_expression = ", ".join(strings_to_join)
        if (
            len(indented_single_line_expression) + child_context.indent
            <= context.max_line_length
        ):
            return [
                (
                    expression_context.prefix_line,
                    "{}{}".format(
                        context.indent_string, expression_context.prefix_string
                    ),
                ),
                (
                    a_list[-1].end_line
                    if len(a_list) > 0
                    else expression_context.suffix_line,
                    "{}{}".format(
                        child_context.indent_string, indented_single_line_expression
                    ),
                ),
                (
                    a_list[-1].end_line
                    if len(a_list) > 0
                    else expression_context.suffix_line,
                    "{}{}".format(
                        context.indent_string, expression_context.suffix_string
                    ),
                ),
            ]
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}".format(context.indent_string, expression_context.prefix_string),
        )
    ]  # type: FormattedLines
    trailing_comma_present = is_trailing_comma(a_list[-1]) if len(a_list) > 0 else False
    for i, element in enumerate(elements):
        suffix = "," if i != len(elements) - 1 or trailing_comma_present else ""
        child_expression_context = ExpressionContext("", element.line, suffix)
        lines, _ = _format_standalone_expression(
            element, child_expression_context, child_context
        )
        formatted_lines += lines
    formatted_lines.append(
        (
            expression_context.suffix_line
            if expression_context.suffix_line is not None
            else a_list[-1].end_line,
            "{}{}".format(context.indent_string, expression_context.suffix_string),
        )
    )
    return formatted_lines


def _format_standalone_expression(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> Outcome:
    expression = remove_outer_parentheses(expression)
    return _format_concrete_expression(expression, expression_context, context)


def _format_concrete_expression(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> Outcome:
    if is_foldable(expression):
        return _format_foldable(expression, expression_context, context)
    return (
        [
            (
                expression_context.prefix_line,
                "{}{}{}{}".format(
                    context.indent_string,
                    expression_context.prefix_string,
                    expression_to_str(expression),
                    expression_context.suffix_string,
                ),
            )
        ],
        expression_context.prefix_line,
    )


def _format_foldable(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> Outcome:
    if is_expression_forcing_multiple_lines(expression, context.standalone_comments):
        return _format_foldable_to_multiple_lines(
            expression, expression_context, context
        )
    single_line_expression = expression_to_str(expression)
    single_line_length = (
        context.indent
        + len(expression_context.prefix_string)
        + len(single_line_expression)
        + len(expression_context.suffix_string)
    )
    if single_line_length <= context.max_line_length:
        single_line = "{}{}{}{}".format(
            context.indent_string,
            expression_context.prefix_string,
            expression_to_str(expression),
            expression_context.suffix_string,
        )
        return (
            [(expression_context.prefix_line, single_line)],
            expression_context.prefix_line,
        )
    return _format_foldable_to_multiple_lines(expression, expression_context, context)


def _format_foldable_to_multiple_lines(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> Outcome:
    handlers = {
        "assnmnt_expr": _format_assignment_expression_to_multiline_line,
        "test_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "or_test": _format_operator_chain_based_expression_to_multiple_lines,
        "and_test": _format_operator_chain_based_expression_to_multiple_lines,
        "not_test": _format_not_test_to_multiple_lines,
        "content_test": _format_operator_chain_based_expression_to_multiple_lines,
        "comparison": _format_operator_chain_based_expression_to_multiple_lines,
        "bitw_or": _format_operator_chain_based_expression_to_multiple_lines,
        "bitw_xor": _format_operator_chain_based_expression_to_multiple_lines,
        "bitw_and": _format_operator_chain_based_expression_to_multiple_lines,
        "shift_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "arith_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "mdr_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "neg_expr": partial(_append_to_expression_context_and_pass, ""),
        "bitw_not": partial(_append_to_expression_context_and_pass, ""),
        "type_test": _format_operator_chain_based_expression_to_multiple_lines,
        "type_cast": _format_operator_chain_based_expression_to_multiple_lines,
        "standalone_call": _format_call_expression_to_multiline_line,
        "getattr_call": _format_call_expression_to_multiline_line,
        "getattr": _format_attribute_expression_to_multiple_lines,
        "subscr_expr": _format_subscription_to_multiple_lines,
        "par_expr": _format_parentheses_to_multiple_lines,
        "array": _format_array_to_multiple_lines,
        "string": _format_string_to_multiple_lines,
        "dict": _format_dict_to_multiple_lines,
        "kv_pair": _format_kv_pair_to_multiple_lines,
        # fake expressions:
        "func_arg_regular": _format_func_arg_to_multiple_lines,
        "func_arg_inf": _format_func_arg_to_multiple_lines,
        "func_arg_typed": _format_func_arg_to_multiple_lines,
    }  # type: Dict[str, Callable]
    return handlers[expression.data](expression, expression_context, context)


def _format_array_to_multiple_lines(
    array: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    new_expression_context = ExpressionContext(
        "{}[".format(expression_context.prefix_string),
        expression_context.prefix_line,
        "]{}".format(expression_context.suffix_string),
        array.end_line,
    )
    return (
        format_comma_separated_list(array.children, new_expression_context, context),
        array.end_line,
    )


def _format_dict_to_multiple_lines(
    a_dict: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    new_expression_context = ExpressionContext(
        "{}{{".format(expression_context.prefix_string),
        expression_context.prefix_line,
        "}}{}".format(expression_context.suffix_string),
        a_dict.end_line,
    )
    return (
        format_comma_separated_list(a_dict.children, new_expression_context, context),
        a_dict.end_line,
    )


def _format_kv_pair_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    concrete_expression = expression.children[0]
    suffix = ":" if concrete_expression.data == "c_dict_element" else ""
    key_expression_context = ExpressionContext(
        expression_context.prefix_string, expression_context.prefix_line, suffix
    )
    key_lines, _ = _format_standalone_expression(
        concrete_expression.children[0], key_expression_context, context
    )
    if concrete_expression.data == "c_dict_element":
        value_expression_context = ExpressionContext(
            "", -1, expression_context.suffix_string
        )
        value_lines, _ = _format_standalone_expression(
            concrete_expression.children[1], value_expression_context, context
        )
        return (key_lines + value_lines, concrete_expression.end_line)
    last_key_line_no, last_key_line = key_lines[-1]
    value_expression_context = ExpressionContext(
        "{} = ".format(last_key_line.strip()),  # to overcome godot bug #35416
        last_key_line_no,  # type: ignore
        expression_context.suffix_string,
    )
    value_lines, last_processed_line_no = _format_standalone_expression(
        concrete_expression.children[1], value_expression_context, context
    )
    return (key_lines[:-1] + value_lines, last_processed_line_no)


def _format_parentheses_to_multiple_lines(
    par_expr: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    new_expression_context = ExpressionContext(
        "{}(".format(expression_context.prefix_string),
        expression_context.prefix_line,
        "){}".format(expression_context.suffix_string),
        par_expr.end_line,
    )
    return (
        _format_standalone_expression(
            par_expr.children[0],
            new_expression_context,
            context,
        )[0],
        par_expr.end_line,
    )


def _format_string_to_multiple_lines(
    string: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    long_string = string.children[0]
    lines = long_string.value.splitlines()
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}{}".format(
                context.indent_string, expression_context.prefix_string, lines[0]
            ),
        )
    ]  # type: FormattedLines
    for middle_line in lines[1:-1]:
        formatted_lines.append((string.line, middle_line))
    formatted_lines.append(
        (string.line, "{}{}".format(lines[-1], expression_context.suffix_string))
    )
    return (formatted_lines, string.line)


def _format_not_test_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    if expression.children[0].value == "!":
        return _append_to_expression_context_and_pass(
            "", expression, expression_context, context
        )
    return _append_to_expression_context_and_pass(
        " ", expression, expression_context, context
    )


def _format_assignment_expression_to_multiline_line(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    new_expression_context = ExpressionContext(
        "{}{} {} ".format(
            expression_context.prefix_string,
            expression_to_str(expression.children[0]),
            expression_to_str(expression.children[1]),
        ),
        expression_context.prefix_line,
        expression_context.suffix_string,
    )
    return _format_concrete_expression(
        expression.children[2], new_expression_context, context
    )


def _format_func_arg_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    if expression.data == "func_arg_regular" and len(expression.children) == 1:
        return _format_concrete_expression(
            expression.children[0], expression_context, context
        )
    if expression.data == "func_arg_typed" and len(expression.children) == 2:
        return (
            [
                (
                    expression.children[1].line,
                    "{}{}".format(context.indent_string, expression_to_str(expression)),
                )
            ],
            expression.children[1].line,
        )
    template = {
        "func_arg_regular": "{} = ",
        "func_arg_inf": "{} := ",
        "func_arg_typed": "{{}}: {} = ".format(expression.children[1]),
    }[expression.data]
    new_expression_context = ExpressionContext(
        template.format(expression.children[0].value),
        expression_context.prefix_line,
        expression_context.suffix_string,
    )
    return format_expression(expression.children[-1], new_expression_context, context)


def _format_call_expression_to_multiline_line(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    dot = "." if has_leading_dot(expression) else ""
    offset = 1 if has_leading_dot(expression) else 0
    callee_node = expression.children[0 + offset]
    callee = expression_to_str(callee_node)
    list_is_empty = len(expression.children) == 3 + offset
    if list_is_empty:
        return (
            [
                (
                    expression_context.prefix_line,
                    "{}{}{}(){}".format(
                        context.indent_string,
                        expression_context.prefix_string,
                        callee,
                        expression_context.suffix_string,
                    ),
                )
            ],
            expression.end_line,
        )
    new_expression_context = ExpressionContext(
        "{}{}{}(".format(expression_context.prefix_string, dot, callee),
        callee_node.line,
        "){}".format(expression_context.suffix_string),
        expression.end_line,
    )
    return (
        format_comma_separated_list(
            expression.children[2 + offset :: 2], new_expression_context, context
        ),
        expression.end_line,
    )


def _format_subscription_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    subscriptee_expression_context = ExpressionContext(
        expression_context.prefix_string, expression_context.prefix_line, ""
    )
    subscriptee = expression.children[0]
    subscriptee_lines, last_line = _format_concrete_expression(
        subscriptee, subscriptee_expression_context, context
    )
    subscript_expression_context = ExpressionContext(
        "{}[".format(subscriptee_lines[-1][1].strip()),
        last_line,
        "]{}".format(expression_context.suffix_string),
    )
    subscript = expression.children[1]
    subscript_lines, _ = _format_standalone_expression(
        subscript, subscript_expression_context, context
    )
    return (subscriptee_lines[:-1] + subscript_lines, expression.end_line)


def _format_attribute_expression_to_multiple_lines(
    expression: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> Outcome:
    suffix = ".".join(expression.children[2::2])
    base_expression_context = ExpressionContext(
        expression_context.prefix_string,
        expression_context.prefix_line,
        ".{}{}".format(suffix, expression_context.suffix_string),
    )
    base = expression.children[0]
    return _format_concrete_expression(base, base_expression_context, context)


def _format_operator_chain_based_expression_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    inside_par = expression_context.prefix_string.endswith(
        "("
    ) and expression_context.suffix_string.startswith(")")
    lpar = "" if inside_par else "("
    rpar = "" if inside_par else ")"
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}{}".format(
                context.indent_string, expression_context.prefix_string, lpar
            ),
        )
    ]  # type: FormattedLines
    child_context = context.create_child_context(expression_context.prefix_line)
    value = expression.children[0]
    lines, _ = _format_concrete_expression(
        value, ExpressionContext("", value.line, ""), child_context
    )
    formatted_lines += lines
    operator_expr_chain = zip(expression.children[1::2], expression.children[2::2])
    for operator, child in operator_expr_chain:
        lines, _ = _format_concrete_expression(
            child,
            ExpressionContext("{} ".format(operator.value), child.line, ""),
            child_context,
        )
        formatted_lines += lines
    formatted_lines.append(
        (
            expression.children[-1].line,
            "{}{}{}".format(
                context.indent_string, rpar, expression_context.suffix_string
            ),
        )
    )
    return (formatted_lines, expression.children[-1].line)


def _append_to_expression_context_and_pass(
    spacing: str,
    expression: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> Outcome:
    str_to_append = expression_to_str(expression.children[0])
    new_expression_context = ExpressionContext(
        "{}{}{}".format(expression_context.prefix_string, str_to_append, spacing),
        expression_context.prefix_line,
        expression_context.suffix_string,
    )
    return _format_concrete_expression(
        expression.children[1], new_expression_context, context
    )
