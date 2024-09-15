from typing import List

from lark import Tree, Token

from ..common.types import Node
from .expression_utils import (
    is_any_comma,
    is_any_parentheses,
    remove_outer_parentheses,
    has_trailing_comma,
)
from .function_statement_to_str import function_statement_to_str


def standalone_expression_to_str(expression: Node) -> str:
    expression = remove_outer_parentheses(expression)
    return expression_to_str(expression)


def expression_to_str(expression: Node) -> str:
    if isinstance(expression, Token):
        token_handlers = {
            "LONG_STRING": _long_string_to_str,
            "LONG_RSTRING": _long_rstring_to_str,
            "REGULAR_STRING": _regular_string_to_str,
            "REGULAR_RSTRING": _regular_rstring_to_str,
        }
        if expression.type in token_handlers:
            return token_handlers[expression.type](expression)
        return expression.value
    return {
        "expr": lambda e: standalone_expression_to_str(e.children[0]),
        "assnmnt_expr": _operator_chain_based_expression_to_str,
        "test_expr": _operator_chain_based_expression_to_str,
        "asless_test_expr": _operator_chain_based_expression_to_str,
        "or_test": _operator_chain_based_expression_to_str,
        "asless_or_test": _operator_chain_based_expression_to_str,
        "and_test": _operator_chain_based_expression_to_str,
        "asless_and_test": _operator_chain_based_expression_to_str,
        "asless_actual_not_test": lambda e: "{}{}{}".format(
            expression_to_str(e.children[0]),
            "" if e.children[0].value == "!" else " ",
            expression_to_str(e.children[1]),
        ),
        "not_in_op": lambda _: "not in",
        "content_test": _operator_chain_based_expression_to_str,
        "asless_content_test": _operator_chain_based_expression_to_str,
        "comparison": _operator_chain_based_expression_to_str,
        "asless_comparison": _operator_chain_based_expression_to_str,
        "bitw_or": _operator_chain_based_expression_to_str,
        "asless_bitw_or": _operator_chain_based_expression_to_str,
        "bitw_xor": _operator_chain_based_expression_to_str,
        "asless_bitw_xor": _operator_chain_based_expression_to_str,
        "bitw_and": _operator_chain_based_expression_to_str,
        "asless_bitw_and": _operator_chain_based_expression_to_str,
        "shift_expr": _operator_chain_based_expression_to_str,
        "asless_shift_expr": _operator_chain_based_expression_to_str,
        "arith_expr": _operator_chain_based_expression_to_str,
        "asless_arith_expr": _operator_chain_based_expression_to_str,
        "mdr_expr": _operator_chain_based_expression_to_str,
        "asless_mdr_expr": _operator_chain_based_expression_to_str,
        "asless_actual_neg_expr": lambda e: f"-{expression_to_str(e.children[1])}",
        "asless_actual_bitw_not": lambda e: f"~{expression_to_str(e.children[1])}",
        "pow_expr": _operator_chain_based_expression_to_str,
        "asless_pow_expr": _operator_chain_based_expression_to_str,
        "type_test": _operator_chain_based_expression_to_str,
        "asless_type_test": _operator_chain_based_expression_to_str,
        "actual_type_cast": _operator_chain_based_expression_to_str,
        "await_expr": lambda e: "{} {}".format(
            " ".join(t.value for t in e.children[:-1]),
            expression_to_str(e.children[-1]),
        ),
        "standalone_call": _standalone_call_to_str,
        "getattr_call": _getattr_call_to_str,
        "getattr": lambda e: "".join(map(expression_to_str, e.children)),
        "subscr_expr": _subscription_to_str,
        "par_expr": lambda e: f"({standalone_expression_to_str(e.children[0])})",
        "array": _array_to_str,
        "dict": _dict_to_str,
        "c_dict_element": _dict_element_to_str,
        "eq_dict_element": _dict_element_to_str,
        "string": lambda e: expression_to_str(e.children[0]),
        "rstring": lambda e: f"r{expression_to_str(e.children[0])}",
        "get_node": lambda e: f"${expression_to_str(e.children[0])}",
        "path": lambda e: "".join([name_token.value for name_token in e.children]),
        "node_path": lambda e: f"^{expression_to_str(e.children[0])}",
        "unique_node_path": lambda e: "".join(
            [expression_to_str(n) for n in e.children]
        ),
        "string_name": lambda e: f"&{expression_to_str(e.children[0])}",
        "lambda": _lambda_to_str,
        "lambda_header": _lambda_header_to_str,
        # fake expressions:
        "func_args": _args_to_str,
        "func_arg_regular": lambda e: "{}{}".format(
            e.children[0].value,
            " = {}".format(standalone_expression_to_str(e.children[1]))
            if len(e.children) > 1
            else "",
        ),
        "func_arg_inf": lambda e: "{} := {}".format(
            e.children[0].value, standalone_expression_to_str(e.children[1])
        ),
        "func_arg_typed": lambda e: "{}: {}{}".format(
            e.children[0].value,
            e.children[1].value,
            f" = {standalone_expression_to_str(e.children[2])}"
            if len(e.children) > 2
            else "",
        ),
        "enum_body": _enum_body_to_str,
        "enum_element": _enum_element_to_str,
        "signal_args": _args_to_str,
        "signal_arg_regular": lambda e: e.children[0].value,
        "signal_arg_typed": lambda e: "{}: {}".format(
            e.children[0].value,
            e.children[1].value,
        ),
        "comma_separated_list": lambda e: _arguments_to_str(e.children),
        "contextless_comma_separated_list": lambda e: _arguments_to_str(e.children),
        "contextless_operator_chain_based_expression": (
            _operator_chain_based_expression_to_str
        ),
        "trailing_comma": lambda _: "",
        "annotation": _annotation_to_str,
        "annotation_args": _annotation_args_to_str,
        "non_foldable_dot_chain": lambda e: "".join(map(expression_to_str, e.children)),
        "actual_getattr_call": _getattr_call_to_str,
        "actual_subscr_expr": _subscription_to_str,
        "property_custom_getter_args": lambda _: "()",
        # patterns (fake expressions):
        "list_pattern": lambda e: ", ".join(map(expression_to_str, e.children)),
        "test_pattern": _operator_chain_based_expression_to_str,
        "or_pattern": _operator_chain_based_expression_to_str,
        "and_pattern": _operator_chain_based_expression_to_str,
        "not_pattern": lambda e: "{}{}{}".format(
            expression_to_str(e.children[0]),
            "" if e.children[0].value == "!" else " ",
            expression_to_str(e.children[1]),
        ),
        "comp_pattern": _operator_chain_based_expression_to_str,
        "bitw_or_pattern": _operator_chain_based_expression_to_str,
        "bitw_xor_pattern": _operator_chain_based_expression_to_str,
        "bitw_and_pattern": _operator_chain_based_expression_to_str,
        "shift_pattern": _operator_chain_based_expression_to_str,
        "arith_pattern": _operator_chain_based_expression_to_str,
        "mdr_pattern": _operator_chain_based_expression_to_str,
        "neg_pattern": lambda e: f"-{expression_to_str(e.children[1])}",
        "bitw_not_pattern": lambda e: f"~{expression_to_str(e.children[1])}",
        "attr_pattern": lambda e: ".".join(map(expression_to_str, e.children[::2])),
        "call_pattern": lambda e: "{}({})".format(
            expression_to_str(e.children[0]), expression_to_str(e.children[1])
        ),
        "par_pattern": lambda e: f"({expression_to_str(e.children[0])})",
        "var_capture_pattern": lambda e: f"var {expression_to_str(e.children[0])}",
        "etc_pattern": lambda _: "..",
        "wildcard_pattern": lambda _: "_",
        "array_pattern": _array_to_str,
        "dict_pattern": _dict_to_str,
        "kv_pair_pattern": lambda e: "{}: {}".format(
            expression_to_str(e.children[0]), expression_to_str(e.children[1])
        ),
    }[expression.data](expression)


def _operator_chain_based_expression_to_str(expression: Tree) -> str:
    operator_expr_chain = zip(expression.children[1::2], expression.children[2::2])

    def _padding(operator):
        return "" if expression_to_str(operator).startswith(".") else " "

    chain = [
        "{}{}{}{}".format(
            _padding(operator),
            expression_to_str(operator),
            _padding(operator),
            expression_to_str(expr),
        )
        for operator, expr in operator_expr_chain
    ]
    first_expr = expression.children[0]
    return "{}{}".format(expression_to_str(first_expr), "".join(chain))


def _standalone_call_to_str(call: Tree) -> str:
    callee = expression_to_str(call.children[0])
    arguments = _arguments_to_str(call.children[1:])
    return f"{callee}({arguments})"


def _getattr_call_to_str(call: Tree) -> str:
    a_getattr = expression_to_str(call.children[0])
    arguments = _arguments_to_str(call.children[1:])
    return f"{a_getattr}({arguments})"


def _arguments_to_str(arguments: List[Node]) -> str:
    return ", ".join(
        [
            standalone_expression_to_str(argument)
            for argument in arguments
            if not is_any_parentheses(argument) and not is_any_comma(argument)
        ]
    )


def _annotation_to_str(annotation: Tree) -> str:
    name = expression_to_str(annotation.children[0])
    if len(annotation.children) > 1:
        return f"@{name}{expression_to_str(annotation.children[1])}"
    return f"@{name}"


def _annotation_args_to_str(annotation: Tree) -> str:
    elements = [
        standalone_expression_to_str(child)
        for child in annotation.children
        if not is_any_comma(child)
    ]
    trailing_comma = "," if has_trailing_comma(annotation) else ""
    return "({}{})".format(", ".join(elements), trailing_comma)


def _lambda_to_str(a_lambda: Tree) -> str:
    assert len(a_lambda.children) == 2
    return "{} {}".format(
        expression_to_str(a_lambda.children[0]),
        function_statement_to_str(a_lambda.children[1]),
    )


def _lambda_header_to_str(lambda_header: Tree) -> str:
    has_name = isinstance(lambda_header.children[0], Token)
    optional_name = f" {lambda_header.children[0].value}" if has_name else ""
    arguments = expression_to_str(lambda_header.children[1 if has_name else 0])
    has_type_hint = len(lambda_header.children) == 3 or (
        len(lambda_header.children) == 2 and not has_name
    )
    type_hint_index = 2 if has_name else 1
    optional_type_hint = (
        f" -> {lambda_header.children[type_hint_index]}" if has_type_hint else ""
    )
    return f"func{optional_name}{arguments}{optional_type_hint}:"


def _array_to_str(array: Tree) -> str:
    elements = [
        standalone_expression_to_str(child)
        for child in array.children
        if not is_any_comma(child)
    ]
    trailing_comma = "," if has_trailing_comma(array) else ""
    return "[{}{}]".format(", ".join(elements), trailing_comma)


def _dict_to_str(a_dict: Tree) -> str:
    elements = map(expression_to_str, a_dict.children)
    return "{{{}}}".format(", ".join(elements))


def _subscription_to_str(subscription: Tree) -> str:
    return "{}[{}]".format(
        expression_to_str(subscription.children[0]),
        standalone_expression_to_str(subscription.children[1]),
    )


def _dict_element_to_str(dict_element: Tree) -> str:
    template = "{}: {}" if dict_element.data.startswith("c_dict_") else "{} = {}"
    return template.format(
        standalone_expression_to_str(dict_element.children[0]),
        standalone_expression_to_str(dict_element.children[1]),
    )


def _enum_body_to_str(enum_body: Tree) -> str:
    if len(enum_body.children) == 0:
        return "{}"
    elements = map(expression_to_str, enum_body.children)
    return "{{ {} }}".format(", ".join(elements))


def _enum_element_to_str(enum_element: Tree) -> str:
    name = standalone_expression_to_str(enum_element.children[0])
    if len(enum_element.children) > 1:
        value = standalone_expression_to_str(enum_element.children[1])
        return f"{name} = {value}"
    return name


def _args_to_str(args: Tree) -> str:
    return "({})".format(", ".join(map(expression_to_str, args.children)))


def _long_string_to_str(string: Token) -> str:
    actual_string = string.value
    if actual_string.startswith("'''") and actual_string.endswith("'''"):
        fake_token = Token("REGULAR_STRING", actual_string[2:-2])
        return _regular_string_to_str(fake_token)
    return actual_string


def _long_rstring_to_str(rstring: Token) -> str:
    actual_string = rstring.value
    return _long_string_to_str(Token("LONG_STRING", actual_string[1:]))


def _regular_string_to_str(string: Token) -> str:
    actual_string = string.value
    actual_string_data = actual_string[1:-1]
    quotes_num = actual_string_data.count('"')
    aposes_num = actual_string_data.count("'")
    target = '"' if quotes_num <= aposes_num else "'"
    if target == '"' and actual_string.startswith("'"):
        actual_string_data = actual_string_data.replace("\\'", "'")
        actual_string_data = actual_string_data.replace('"', '\\"')
    if target == "'" and actual_string.startswith('"'):
        actual_string_data = actual_string_data.replace('\\"', '"')
        actual_string_data = actual_string_data.replace("'", "\\'")
    return "{}{}{}".format(target, actual_string_data, target)  # pylint: disable=W1308


def _regular_rstring_to_str(rstring: Token) -> str:
    actual_string = rstring.value
    return _regular_string_to_str(Token("REGULAR_STRING", actual_string[1:]))
