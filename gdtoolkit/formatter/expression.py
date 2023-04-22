from typing import Dict, Callable, List, Optional

from lark import Tree, Token
from lark.tree import Meta

from ..common.utils import get_line, get_end_line
from ..common.types import Node
from .context import Context, ExpressionContext
from .types import Outcome, FormattedLines
from .expression_utils import (
    remove_outer_parentheses,
    is_foldable,
    is_expression_forcing_multiple_lines,
    is_any_comma,
    is_trailing_comma,
)
from .expression_to_str import expression_to_str
from .constants import INDENT_SIZE


def format_expression(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    concrete_expression = expression.children[0]
    return (
        _format_standalone_expression(concrete_expression, expression_context, context),
        get_end_line(expression),
    )


def format_concrete_expression(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    return (
        _format_concrete_expression(expression, expression_context, context),
        get_end_line(expression),
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
        assert isinstance(expression, Tree)
        return _format_foldable(expression, expression_context, context)  # type: ignore
    return _format_concrete_expression_to_single_line(
        expression, expression_context, context
    )


def _format_concrete_expression_to_single_line(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
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
    single_line_number, single_line = _format_concrete_expression_to_single_line(
        expression, expression_context, context
    )[0]
    single_line_length = len(single_line.replace("\t", " " * INDENT_SIZE))
    if single_line_length <= context.max_line_length:
        return [(single_line_number, single_line)]
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
        "asless_actual_neg_expr": lambda e, ec, c: _append_to_expression_context_and_pass(
            f"{expression_to_str(e.children[0])}", e.children[1], ec, c
        ),
        "asless_actual_bitw_not": lambda e, ec, c: _append_to_expression_context_and_pass(
            f"{expression_to_str(e.children[0])}", e.children[1], ec, c
        ),
        "pow_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_pow_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "type_test": _format_operator_chain_based_expression_to_multiple_lines,
        "asless_type_test": _format_operator_chain_based_expression_to_multiple_lines,
        "actual_type_cast": _format_operator_chain_based_expression_to_multiple_lines,
        "await_expr": _format_await_expression_to_multiple_lines,
        "standalone_call": _format_call_expression_to_multiple_lines,
        "getattr_call": _collapse_getattr_tree_to_dot_chain_and_format_to_multiple_lines,
        "getattr": _collapse_getattr_tree_to_dot_chain_and_format_to_multiple_lines,
        "subscr_expr": _collapse_subscr_expr_tree_to_dot_chain_and_format_to_multiple_lines,
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
        "inline_lambda": _format_inline_lambda_to_multiple_lines,
        "lambda_header": _format_lambda_header_to_multiple_lines,
        "inline_lambda_statements": _format_inline_lambda_statements_to_multiple_lines,
        "pass_stmt": _format_concrete_expression_to_single_line,
        "return_stmt": lambda e, ec, c: _append_to_expression_context_and_pass_standalone(
            "return ", e.children[0], ec, c
        ),
        "expr_stmt": lambda e, ec, c: _format_standalone_expression(
            e.children[0].children[0], ec, c
        ),
        "func_var_stmt": lambda e, ec, c: _format_standalone_expression(
            e.children[0], ec, c
        ),
        "func_var_empty": _format_concrete_expression_to_single_line,
        "func_var_assigned": lambda e, ec, c: _append_to_expression_context_and_pass_standalone(
            f"var {expression_to_str(e.children[0])} = ", e.children[1], ec, c
        ),
        "func_var_typed": _format_concrete_expression_to_single_line,
        "func_var_typed_assgnd": lambda e, ec, c: _append_to_expression_context_and_pass_standalone(
            f"var {expression_to_str(e.children[0])}: {expression_to_str(e.children[1])} = ",
            e.children[2],
            ec,
            c,
        ),
        "func_var_inf": lambda e, ec, c: _append_to_expression_context_and_pass_standalone(
            f"var {expression_to_str(e.children[0])} := ", e.children[1], ec, c
        ),
        "dot_chain": _format_dot_chain_to_multiple_lines,
        "actual_getattr_call": _format_call_expression_to_multiple_lines,
        "actual_subscr_expr": _format_subscription_to_multiple_lines,
    }  # type: Dict[str, Callable]
    return handlers[expression.data](expression, expression_context, context)


def _format_array_to_multiple_lines(
    array: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    new_expression_context = ExpressionContext(
        f"{expression_context.prefix_string}[",
        expression_context.prefix_line,
        f"]{expression_context.suffix_string}",
        get_end_line(array),
    )
    return _format_comma_separated_list(array.children, new_expression_context, context)


def _format_dict_to_multiple_lines(
    a_dict: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    new_expression_context = ExpressionContext(
        f"{expression_context.prefix_string}{{",
        expression_context.prefix_line,
        f"}}{expression_context.suffix_string}",
        get_end_line(a_dict),
    )
    return _format_comma_separated_list(
        a_dict.children, new_expression_context, context
    )


def _format_args_to_multiple_lines(
    args: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    new_expression_context = ExpressionContext(
        f"{expression_context.prefix_string}(",
        expression_context.prefix_line,
        f"){expression_context.suffix_string}",
        get_end_line(args),
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
        f"{expression_context.prefix_string}(",
        expression_context.prefix_line,
        f"){expression_context.suffix_string}",
        get_end_line(par_expr),
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
        formatted_lines.append((get_line(string), middle_line))
    formatted_lines.append(
        (get_line(string), f"{lines[-1]}{expression_context.suffix_string}")
    )
    return formatted_lines


def _format_not_test_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    spacing = "" if expression.children[0].value == "!" else " "
    return _append_to_expression_context_and_pass(
        f"{expression_to_str(expression.children[0])}{spacing}",
        expression.children[1],
        expression_context,
        context,
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
                get_line(expression.children[1]),
                f"{context.indent_string}{expression_to_str(expression)}",
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
        get_line(callee_node),
        "){}".format(expression_context.suffix_string),
        get_end_line(expression),
    )
    return _format_comma_separated_list(
        expression.children[1:], new_expression_context, context
    )


def _collapse_getattr_tree_to_dot_chain_and_format_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    return _format_foldable_to_multiple_lines(
        _collapse_getattr_tree_to_dot_chain(expression), expression_context, context
    )


def _collapse_subscr_expr_tree_to_dot_chain_and_format_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    dot_chain = _collapse_subscr_expr_tree_to_dot_chain(expression)
    if len(dot_chain.children) == 1:
        dot_chain = dot_chain.children[0]
    return _format_foldable_to_multiple_lines(dot_chain, expression_context, context)


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
    assert last_line is not None
    subscript_expression_context = ExpressionContext(
        f"{subscriptee_lines[-1][1].strip()}[",
        last_line,  # type: ignore
        f"]{expression_context.suffix_string}",
        expression_context.suffix_line,
    )
    subscript = expression.children[1]
    subscript_lines = _format_concrete_expression(
        subscript, subscript_expression_context, context
    )
    return subscriptee_lines[:-1] + subscript_lines


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
            get_end_line(expression.children[-1]),
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
        value, ExpressionContext("", get_line(value), "", get_end_line(value)), context
    )
    formatted_lines += lines
    operator_expr_chain = zip(expression.children[1::2], expression.children[2::2])
    for operator, child in operator_expr_chain:
        lines = _format_concrete_expression(
            child,
            ExpressionContext(
                f"{operator.value} ", get_line(child), "", get_end_line(child)
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
            f"{context.indent_string}{expression_context.prefix_string}",
        )
    ]  # type: FormattedLines
    if len(a_list) > 0:
        formatted_lines += _format_concrete_expression(
            fake_expression, child_expression_context, child_context
        )
    formatted_lines.append(
        (
            expression_context.suffix_line,
            f"{context.indent_string}{expression_context.suffix_string}",
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
            "", get_line(element), suffix, get_end_line(element)
        )
        lines = _format_standalone_expression(
            element, child_expression_context, context
        )
        formatted_lines += lines
    return formatted_lines


def _append_to_expression_context(
    str_to_append: str,
    expression_context: ExpressionContext,
) -> ExpressionContext:
    return ExpressionContext(
        f"{expression_context.prefix_string}{str_to_append}",
        expression_context.prefix_line,
        expression_context.suffix_string,
        expression_context.suffix_line,
    )


def _append_to_expression_context_and_pass(
    str_to_append: str,
    expression: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> FormattedLines:
    new_expression_context = _append_to_expression_context(
        str_to_append, expression_context
    )
    return _format_concrete_expression(expression, new_expression_context, context)


def _append_to_expression_context_and_pass_standalone(
    str_to_append: str,
    expression: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> FormattedLines:
    new_expression_context = _append_to_expression_context(
        str_to_append, expression_context
    )
    return format_expression(expression, new_expression_context, context)[0]


def _format_await_expression_to_multiple_lines(
    expression: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> FormattedLines:
    str_to_append = " ".join(token.value for token in expression.children[:-1])
    new_expression_context = ExpressionContext(
        f"{expression_context.prefix_string}{str_to_append} ",
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
        return [(get_line(annotation), f"{context.indent_string}@{annotation_name}")]
    new_expression_context = ExpressionContext(
        f"@{annotation_name}", get_line(annotation), "", -1
    )
    return _format_concrete_expression(
        annotation.children[-1], new_expression_context, context
    )


def _format_inline_lambda_to_multiple_lines(
    inline_lambda: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> FormattedLines:
    expression_context_for_header = ExpressionContext(
        expression_context.prefix_string, expression_context.prefix_line, "", -1
    )
    header_lines = _format_concrete_expression(
        inline_lambda.children[0], expression_context_for_header, context
    )
    last_header_line_number, last_header_line = header_lines[-1]
    assert last_header_line_number is not None
    expression_context_for_statements = ExpressionContext(
        f"{last_header_line.strip()} ",
        last_header_line_number,  # type:ignore
        expression_context.suffix_string,
        expression_context.suffix_line,
    )
    fake_meta = Meta()
    fake_meta.line = get_line(inline_lambda.children[1])
    fake_meta.end_line = get_end_line(inline_lambda.children[-1])
    fake_expression = Tree(
        "inline_lambda_statements", inline_lambda.children[1:], fake_meta
    )
    statement_lines = _format_concrete_expression(
        fake_expression, expression_context_for_statements, context
    )
    return header_lines[:-1] + statement_lines


def _format_lambda_header_to_multiple_lines(
    lambda_header: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> FormattedLines:
    append_to_prefix = (
        f"func {lambda_header.children[0].value}"
        if isinstance(lambda_header.children[0], Token)
        else "func"
    )
    args_offset = 1 if isinstance(lambda_header.children[0], Token) else 0
    theres_something_after_args = len(lambda_header.children) > args_offset + 1
    optional_type_hint = (
        f" -> {lambda_header.children[args_offset+1]}"
        if theres_something_after_args
        else ""
    )
    prepend_to_suffix = f"{optional_type_hint}:"
    new_expression_context = ExpressionContext(
        f"{expression_context.prefix_string}{append_to_prefix}",
        expression_context.prefix_line,
        f"{prepend_to_suffix}{expression_context.suffix_string}",
        expression_context.suffix_line,
    )
    return _format_concrete_expression(
        lambda_header.children[args_offset], new_expression_context, context
    )


def _format_inline_lambda_statements_to_multiple_lines(
    inline_lambda_statements: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> FormattedLines:
    lambda_statements = inline_lambda_statements.children
    if len(lambda_statements) == 1:
        return _format_concrete_expression(
            lambda_statements[0], expression_context, context
        )
    expression_context_for_first_statement = ExpressionContext(
        expression_context.prefix_string, expression_context.prefix_line, "", -1
    )
    first_statement_formatted_lines = _format_concrete_expression(
        lambda_statements[0], expression_context_for_first_statement, context
    )
    last_line_number, last_line = first_statement_formatted_lines[-1]
    assert last_line_number is not None
    remaining_statements_prefix = last_line.strip()
    remaining_statements_expression_context = ExpressionContext(
        f"{remaining_statements_prefix} ; ",
        last_line_number,  # type: ignore
        expression_context.suffix_string,
        expression_context.suffix_line,
    )
    fake_meta = Meta()
    fake_meta.line = get_line(lambda_statements[1])
    fake_meta.end_line = get_end_line(lambda_statements[-1])
    fake_expression = Tree("inline_lambda_statements", lambda_statements[1:], fake_meta)
    return first_statement_formatted_lines[:-1] + _format_concrete_expression(
        fake_expression, remaining_statements_expression_context, context
    )


def _collapse_getattr_tree_to_dot_chain(expression: Tree) -> Tree:
    reversed_dot_chain_children = []  # type: List[Node]
    pending_getattr_call_to_match = None
    next_expression_to_process = expression  # type: Optional[Node]
    while next_expression_to_process is not None:
        if isinstance(next_expression_to_process, Token):
            reversed_dot_chain_children.append(next_expression_to_process)
            next_expression_to_process = None
        elif next_expression_to_process.data == "getattr_call":
            pending_getattr_call_to_match = next_expression_to_process
            next_expression_to_process = next_expression_to_process.children[0]
        elif next_expression_to_process.data == "getattr":
            if pending_getattr_call_to_match is None:
                reversed_dot_chain_children += reversed(
                    next_expression_to_process.children[1:]
                )
            else:
                matching_attr = next_expression_to_process.children[-1]
                fake_meta = Meta()
                fake_meta.line = get_line(matching_attr)
                fake_meta.end_line = get_end_line(pending_getattr_call_to_match)
                fake_expression = Tree(
                    "actual_getattr_call",
                    [matching_attr] + pending_getattr_call_to_match.children[1:],
                    fake_meta,
                )
                pending_getattr_call_to_match = None
                reversed_dot_chain_children.append(fake_expression)
                reversed_dot_chain_children += reversed(
                    next_expression_to_process.children[1:-1]
                )
            next_expression_to_process = next_expression_to_process.children[0]
        elif next_expression_to_process.data == "subscr_expr":
            sub_dot_chain = _collapse_subscr_expr_tree_to_dot_chain(
                next_expression_to_process
            )
            reversed_dot_chain_children = reversed_dot_chain_children + list(
                reversed(sub_dot_chain.children)
            )
            next_expression_to_process = None
        else:
            reversed_dot_chain_children.append(next_expression_to_process)
            next_expression_to_process = None
    dot_chain_children = list(reversed(reversed_dot_chain_children))
    fake_meta = Meta()
    fake_meta.line = get_line(dot_chain_children[0])
    fake_meta.end_line = get_end_line(dot_chain_children[-1])
    fake_expression = Tree(
        "dot_chain",
        dot_chain_children,
        fake_meta,
    )
    return fake_expression


def _collapse_subscr_expr_tree_to_dot_chain(expression: Tree) -> Tree:
    subscriptee = expression.children[0]
    subscript_to_match = expression.children[1]
    collapsers = {
        "subscr_expr": _collapse_subscr_expr_tree_to_dot_chain,
        "getattr": _collapse_getattr_tree_to_dot_chain,
        "getattr_call": _collapse_getattr_tree_to_dot_chain,
    }
    sub_dot_chain = (
        collapsers[subscriptee.data](subscriptee).children
        if isinstance(subscriptee, Tree) and subscriptee.data in collapsers
        else [subscriptee]
    )
    matching_expr = sub_dot_chain[-1]
    fake_meta = Meta()
    fake_meta.line = get_line(matching_expr)
    fake_meta.end_line = get_end_line(expression)
    fake_expression = Tree(
        "actual_subscr_expr",
        [matching_expr, subscript_to_match],
        fake_meta,
    )

    dot_chain_children = sub_dot_chain[:-1] + [fake_expression]
    fake_meta = Meta()
    fake_meta.line = get_line(dot_chain_children[0])
    fake_meta.end_line = get_end_line(dot_chain_children[-1])
    fake_expression = Tree(
        "dot_chain",
        dot_chain_children,
        fake_meta,
    )
    return fake_expression


def _format_dot_chain_to_multiple_lines(
    dot_chain: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> FormattedLines:
    if is_expression_forcing_multiple_lines(dot_chain, context.standalone_comments):
        return _format_operator_chain_based_expression_to_multiple_lines(
            dot_chain, expression_context, context
        )
    lines_formatted_bottom_up = _format_dot_chain_to_multiple_lines_bottom_up(
        dot_chain, expression_context, context
    )
    if all(
        len(line.replace("\t", " " * INDENT_SIZE)) <= context.max_line_length
        for line_number, line in lines_formatted_bottom_up
    ):
        return lines_formatted_bottom_up
    return _format_operator_chain_based_expression_to_multiple_lines(
        dot_chain, expression_context, context
    )


def _format_dot_chain_to_multiple_lines_bottom_up(
    dot_chain: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> FormattedLines:
    last_chain_element = dot_chain.children[-1]
    if isinstance(last_chain_element, Token) or last_chain_element.data not in [
        "actual_getattr_call",
        "actual_subscr_expr",
    ]:
        return _format_operator_chain_based_expression_to_multiple_lines(
            dot_chain, expression_context, context
        )

    fake_meta = Meta()
    fake_meta.line = get_line(dot_chain)
    fake_meta.end_line = get_end_line(last_chain_element.children[0])
    new_dot_chain = Tree(
        "non_foldable_dot_chain",
        dot_chain.children[:-1] + [last_chain_element.children[0]],
        fake_meta,
    )

    fake_meta = Meta()
    fake_meta.line = get_line(new_dot_chain)
    fake_meta.end_line = get_end_line(last_chain_element)
    new_actual_expr = Tree(
        last_chain_element.data,
        [new_dot_chain] + last_chain_element.children[1:],
        fake_meta,
    )
    return _format_concrete_expression(new_actual_expr, expression_context, context)
