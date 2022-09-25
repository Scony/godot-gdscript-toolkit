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
)
from .expression_to_str import expression_to_str


def format_expression(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    concrete_expression = expression.children[0]
    return (
        _format_standalone_expression(concrete_expression, expression_context, context),
        expression.end_line,
    )


def format_concrete_expression(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    return (
        _format_concrete_expression(expression, expression_context, context),
        expression.end_line,
    )


def _format_standalone_expression(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    expression = remove_outer_parentheses(expression)
    return _format_concrete_expression(expression, expression_context, context)


def _format_concrete_expression(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    if is_foldable(expression):
        return _format_foldable(expression, expression_context, context)  # type: ignore
    return [
        (
            expression_context.prefix_line,
            "{}{}{}{}".format(
                context.indent_string,
                expression_context.prefix_string,
                expression_to_str(expression),
                expression_context.suffix_string,
            ),
        )
    ]


def _format_comma_separated_list(
    a_list: List[Node], expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    fake_meta = Meta()
    fake_meta.line = expression_context.prefix_line
    fake_meta.end_line = expression_context.suffix_line
    fake_expression = Tree("comma_separated_list", a_list, fake_meta)
    return _format_concrete_expression(fake_expression, expression_context, context)


def _format_foldable(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
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
        return [(expression_context.prefix_line, single_line)]
    return _format_foldable_to_multiple_lines(expression, expression_context, context)


def _format_foldable_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    handlers = {
        "assnmnt_expr": _format_assignment_expression_to_multiple_lines,
        "test_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_test_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "or_test": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_or_test": _format_operator_chain_based_expression_to_multiple_lines,
        "and_test": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_and_test": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_actual_not_test": _format_not_test_to_multiple_lines,
        "content_test": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_content_test": (
            _format_operator_chain_based_expression_to_multiple_lines
        ),
        "comparison": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_comparison": _format_operator_chain_based_expression_to_multiple_lines,
        "bitw_or": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_bitw_or": _format_operator_chain_based_expression_to_multiple_lines,
        "bitw_xor": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_bitw_xor": _format_operator_chain_based_expression_to_multiple_lines,
        "bitw_and": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_bitw_and": _format_operator_chain_based_expression_to_multiple_lines,
        "shift_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_shift_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "arith_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_arith_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "mdr_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_mdr_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_actual_neg_expr": partial(_append_to_expression_context_and_pass, ""),
        "asless_actual_bitw_not": partial(_append_to_expression_context_and_pass, ""),
        "type_test": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_type_test": _format_operator_chain_based_expression_to_multiple_lines,
        "actual_type_cast": _format_operator_chain_based_expression_to_multiple_lines,
        "await_expr": _format_await_expression_to_multiple_lines,
        "standalone_call": _format_call_expression_to_multiple_lines,
        "getattr_call": _format_call_expression_to_multiple_lines,
        "getattr": _format_attribute_expression_to_multiple_lines,
        "subscr_expr": _format_subscription_to_multiple_lines,
        "par_expr": _format_parentheses_to_multiple_lines,
        "array": _format_array_to_multiple_lines,
        "string": _format_string_to_multiple_lines,
        "dict": _format_dict_to_multiple_lines,
        "c_dict_element": _format_kv_pair_to_multiple_lines,
        "eq_dict_element": _format_kv_pair_to_multiple_lines,
        # fake expressions:
        "func_args": _format_args_to_multiple_lines,
        "func_arg_regular": _format_func_arg_to_multiple_lines,
        "func_arg_inf": _format_func_arg_to_multiple_lines,
        "func_arg_typed": _format_func_arg_to_multiple_lines,
        "enum_body": _format_dict_to_multiple_lines,
        "signal_args": _format_args_to_multiple_lines,
        "comma_separated_list": _format_comma_separated_list_to_multiple_lines,
        "contextless_comma_separated_list": (
            _format_contextless_comma_separated_list_to_multiple_lines
        ),
        "contextless_operator_chain_based_expression": (
            _format_contextless_operator_chain_based_expression_to_multiple_lines
        ),
        "annotation": _format_annotation_to_multiple_lines,
        "annotation_args": _format_args_to_multiple_lines,
    }  # type: Dict[str, Callable]
    return handlers[expression.data](expression, expression_context, context)


def _format_array_to_multiple_lines(
    array: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    new_expression_context = ExpressionContext(
        "{}[".format(expression_context.prefix_string),
        expression_context.prefix_line,
        "]{}".format(expression_context.suffix_string),
        array.end_line,
    )
    return _format_comma_separated_list(array.children, new_expression_context, context)


def _format_dict_to_multiple_lines(
    a_dict: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    new_expression_context = ExpressionContext(
        "{}{{".format(expression_context.prefix_string),
        expression_context.prefix_line,
        "}}{}".format(expression_context.suffix_string),
        a_dict.end_line,
    )
    return _format_comma_separated_list(
        a_dict.children, new_expression_context, context
    )


def _format_args_to_multiple_lines(
    args: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    new_expression_context = ExpressionContext(
        "{}(".format(expression_context.prefix_string),
        expression_context.prefix_line,
        "){}".format(expression_context.suffix_string),
        args.end_line,
    )
    return _format_comma_separated_list(args.children, new_expression_context, context)


def _format_kv_pair_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    suffix = ":" if expression.data == "c_dict_element" else " ="
    key_expression_context = ExpressionContext(
        expression_context.prefix_string,
        expression_context.prefix_line,
        suffix,
        expression_context.suffix_line,
    )
    key_lines = _format_standalone_expression(
        expression.children[0], key_expression_context, context
    )
    value_expression_context = ExpressionContext(
        "", -1, expression_context.suffix_string, expression_context.suffix_line
    )
    value_lines = _format_standalone_expression(
        expression.children[1], value_expression_context, context
    )
    return key_lines + value_lines


def _format_parentheses_to_multiple_lines(
    par_expr: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    new_expression_context = ExpressionContext(
        "{}(".format(expression_context.prefix_string),
        expression_context.prefix_line,
        "){}".format(expression_context.suffix_string),
        par_expr.end_line,
    )
    return _format_standalone_expression(
        par_expr.children[0],
        new_expression_context,
        context,
    )


def _format_string_to_multiple_lines(
    string: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
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
    return formatted_lines


def _format_not_test_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    if expression.children[0].value == "!":
        return _append_to_expression_context_and_pass(
            "", expression, expression_context, context
        )
    return _append_to_expression_context_and_pass(
        " ", expression, expression_context, context
    )


def _format_assignment_expression_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    new_expression_context = ExpressionContext(
        "{}{} {} ".format(
            expression_context.prefix_string,
            expression_to_str(expression.children[0]),
            expression_to_str(expression.children[1]),
        ),
        expression_context.prefix_line,
        expression_context.suffix_string,
        expression_context.suffix_line,
    )
    return _format_concrete_expression(
        expression.children[2], new_expression_context, context
    )


def _format_func_arg_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    if expression.data == "func_arg_regular" and len(expression.children) == 1:
        return _format_concrete_expression(
            expression.children[0], expression_context, context
        )
    if expression.data == "func_arg_typed" and len(expression.children) == 2:
        return [
            (
                expression.children[1].line,
                "{}{}".format(context.indent_string, expression_to_str(expression)),
            )
        ]
    template = {
        "func_arg_regular": "{} = ",
        "func_arg_inf": "{} := ",
        "func_arg_typed": "{{}}: {} = ".format(expression.children[1]),
    }[expression.data]
    new_expression_context = ExpressionContext(
        template.format(expression.children[0].value),
        expression_context.prefix_line,
        expression_context.suffix_string,
        expression_context.suffix_line,
    )
    return format_expression(expression.children[-1], new_expression_context, context)[
        0
    ]


def _format_call_expression_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    callee_node = expression.children[0]
    callee = expression_to_str(callee_node)
    list_is_empty = len(expression.children) == 1
    if list_is_empty:
        return [
            (
                expression_context.prefix_line,
                "{}{}{}(){}".format(
                    context.indent_string,
                    expression_context.prefix_string,
                    callee,
                    expression_context.suffix_string,
                ),
            )
        ]
    new_expression_context = ExpressionContext(
        "{}{}(".format(expression_context.prefix_string, callee),
        callee_node.line,
        "){}".format(expression_context.suffix_string),
        expression.end_line,
    )
    return _format_comma_separated_list(
        expression.children[1:], new_expression_context, context
    )


def _format_subscription_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    subscriptee_expression_context = ExpressionContext(
        expression_context.prefix_string,
        expression_context.prefix_line,
        "",
        expression_context.suffix_line,
    )
    subscriptee = expression.children[0]
    subscriptee_lines = _format_concrete_expression(
        subscriptee, subscriptee_expression_context, context
    )
    last_line = subscriptee_lines[-1][0]
    subscript_expression_context = ExpressionContext(
        "{}[".format(subscriptee_lines[-1][1].strip()),
        last_line,  # type: ignore
        "]{}".format(expression_context.suffix_string),
        expression_context.suffix_line,
    )
    subscript = expression.children[1]
    subscript_lines = _format_standalone_expression(
        subscript, subscript_expression_context, context
    )
    return subscriptee_lines[:-1] + subscript_lines


def _format_attribute_expression_to_multiple_lines(
    expression: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> FormattedLines:
    suffix = ".".join(expression.children[2::2])
    base_expression_context = ExpressionContext(
        expression_context.prefix_string,
        expression_context.prefix_line,
        ".{}{}".format(suffix, expression_context.suffix_string),
        expression_context.suffix_line,
    )
    base = expression.children[0]
    return _format_concrete_expression(base, base_expression_context, context)


def _format_operator_chain_based_expression_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    inside_par = (
        expression_context.prefix_string.endswith("(")
        and expression_context.suffix_string.startswith(")")
    ) or (
        expression_context.prefix_string.endswith("[")
        and expression_context.suffix_string.startswith("]")
    )
    lpar = "" if inside_par else "("
    rpar = "" if inside_par else ")"
    child_context = context.create_child_context(expression_context.prefix_line)
    child_expression_context = ExpressionContext(
        "",
        expression_context.prefix_line,
        "",
        expression_context.suffix_line,
    )
    fake_meta = Meta()
    fake_meta.line = expression_context.prefix_line
    fake_meta.end_line = expression_context.suffix_line
    fake_expression = Tree(
        "contextless_operator_chain_based_expression", expression.children, fake_meta
    )
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}{}".format(
                context.indent_string, expression_context.prefix_string, lpar
            ),
        )
    ]  # type: FormattedLines
    formatted_lines += _format_concrete_expression(
        fake_expression, child_expression_context, child_context
    )
    formatted_lines.append(
        (
            expression.children[-1].line,
            "{}{}{}".format(
                context.indent_string, rpar, expression_context.suffix_string
            ),
        )
    )
    return formatted_lines


def _format_contextless_operator_chain_based_expression_to_multiple_lines(
    expression: Tree, _: ExpressionContext, context: Context
) -> FormattedLines:
    formatted_lines = []  # type: FormattedLines
    value = expression.children[0]
    lines = _format_concrete_expression(
        value, ExpressionContext("", value.line, "", value.end_line), context
    )
    formatted_lines += lines
    operator_expr_chain = zip(expression.children[1::2], expression.children[2::2])
    for operator, child in operator_expr_chain:
        lines = _format_concrete_expression(
            child,
            ExpressionContext(
                "{} ".format(operator.value), child.line, "", child.end_line
            ),
            context,
        )
        formatted_lines += lines
    return formatted_lines


def _format_comma_separated_list_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    a_list = expression.children
    child_context = context.create_child_context(expression_context.prefix_line)
    child_expression_context = ExpressionContext(
        "",
        expression_context.prefix_line,
        "",
        expression_context.suffix_line,
    )
    fake_meta = Meta()
    fake_meta.line = expression_context.prefix_line
    fake_meta.end_line = expression_context.suffix_line
    fake_expression = Tree("contextless_comma_separated_list", a_list, fake_meta)
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}".format(context.indent_string, expression_context.prefix_string),
        )
    ]  # type: FormattedLines
    if len(a_list) > 0:
        formatted_lines += _format_concrete_expression(
            fake_expression, child_expression_context, child_context
        )
    formatted_lines.append(
        (
            expression_context.suffix_line,
            "{}{}".format(context.indent_string, expression_context.suffix_string),
        )
    )
    return formatted_lines


def _format_contextless_comma_separated_list_to_multiple_lines(
    expression: Tree, _: ExpressionContext, context: Context
) -> FormattedLines:
    a_list = expression.children
    elements = [node for node in a_list if not is_any_comma(node)]
    formatted_lines = []  # type: FormattedLines
    trailing_comma_present = is_trailing_comma(a_list[-1]) if len(a_list) > 0 else False
    for i, element in enumerate(elements):
        suffix = "," if i != len(elements) - 1 or trailing_comma_present else ""
        child_expression_context = ExpressionContext(
            "", element.line, suffix, element.end_line
        )
        lines = _format_standalone_expression(
            element, child_expression_context, context
        )
        formatted_lines += lines
    return formatted_lines


def _append_to_expression_context_and_pass(
    spacing: str,
    expression: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> FormattedLines:
    str_to_append = expression_to_str(expression.children[0])
    new_expression_context = ExpressionContext(
        "{}{}{}".format(expression_context.prefix_string, str_to_append, spacing),
        expression_context.prefix_line,
        expression_context.suffix_string,
        expression_context.suffix_line,
    )
    return _format_concrete_expression(
        expression.children[1], new_expression_context, context
    )


def _format_await_expression_to_multiple_lines(
    expression: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> FormattedLines:
    str_to_append = " ".join(token.value for token in expression.children[:-1])
    new_expression_context = ExpressionContext(
        "{}{} ".format(expression_context.prefix_string, str_to_append),
        expression_context.prefix_line,
        expression_context.suffix_string,
        expression_context.suffix_line,
    )
    return _format_concrete_expression(
        expression.children[-1], new_expression_context, context
    )


def _format_annotation_to_multiple_lines(
    annotation: Tree,
    _: ExpressionContext,
    context: Context,
) -> FormattedLines:
    annotation_name = annotation.children[0].value
    if len(annotation.children) == 1:
        return [(annotation.line, f"{context.indent_string}@{annotation_name}")]
    new_expression_context = ExpressionContext(
        f"@{annotation_name}", annotation.line, "", -1
    )
    return _format_concrete_expression(
        annotation.children[-1], new_expression_context, context
    )
