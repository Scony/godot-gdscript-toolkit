from typing import List

from lark import Tree, Token

from .types import Node
from .expression_utils import (
    is_any_comma,
    is_any_parentheses,
    has_leading_dot,
    remove_outer_parentheses,
    has_trailing_comma,
)


def standalone_expression_to_str(expression: Node) -> str:
    expression = remove_outer_parentheses(expression)
    return expression_to_str(expression)


def expression_to_str(expression: Node) -> str:
    if isinstance(expression, Token):
        token_handlers = {
            "LONG_STRING": _long_string_to_str,
            "REGULAR_STRING": _regular_string_to_str,
        }
        if expression.type in token_handlers:
            return token_handlers[expression.type](expression)
        return expression.value
    return {
        "expr": lambda e: standalone_expression_to_str(e.children[0]),
        "assnmnt_expr": _operator_chain_based_expression_to_str,
        "test_expr": _operator_chain_based_expression_to_str,
        "or_test": _operator_chain_based_expression_to_str,
        "and_test": _operator_chain_based_expression_to_str,
        "not_test": lambda e: "{}{}{}".format(
            expression_to_str(e.children[0]),
            "" if e.children[0].value == "!" else " ",
            expression_to_str(e.children[1]),
        ),
        "content_test": _operator_chain_based_expression_to_str,
        "comparison": _operator_chain_based_expression_to_str,
        "bitw_or": _operator_chain_based_expression_to_str,
        "bitw_xor": _operator_chain_based_expression_to_str,
        "bitw_and": _operator_chain_based_expression_to_str,
        "shift_expr": _operator_chain_based_expression_to_str,
        "arith_expr": _operator_chain_based_expression_to_str,
        "mdr_expr": _operator_chain_based_expression_to_str,
        "neg_expr": lambda e: "-{}".format(expression_to_str(e.children[1])),
        "bitw_not": lambda e: "~{}".format(expression_to_str(e.children[1])),
        "type_test": _operator_chain_based_expression_to_str,
        "type_cast": _operator_chain_based_expression_to_str,
        "standalone_call": _standalone_call_to_str,
        "getattr_call": _getattr_call_to_str,
        "getattr": lambda e: "".join(map(expression_to_str, e.children)),
        "subscr_expr": _subscription_to_str,
        "par_expr": lambda e: "({})".format(
            standalone_expression_to_str(e.children[0])
        ),
        "array": _array_to_str,
        "dict": _dict_to_str,
        "kv_pair": lambda e: _dict_element_to_str(e.children[0]),
        "c_dict_element": _dict_element_to_str,
        "eq_dict_element": _dict_element_to_str,
        "string": lambda e: expression_to_str(e.children[0]),
        "node_path": lambda e: "@{}".format(expression_to_str(e.children[0])),
        "get_node": lambda e: "${}".format(expression_to_str(e.children[0])),
        "path": lambda e: "/".join([name_token.value for name_token in e.children]),
        # fake expressions:
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
            " = {}".format(standalone_expression_to_str(e.children[2]))
            if len(e.children) > 2
            else "",
        ),
        "trailing_comma": lambda _: "",
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
        "neg_pattern": lambda e: "-{}".format(expression_to_str(e.children[1])),
        "bitw_not_pattern": lambda e: "~{}".format(expression_to_str(e.children[1])),
        "attr_pattern": lambda e: ".".join(map(expression_to_str, e.children[::2])),
        "call_pattern": lambda e: "{}({})".format(
            expression_to_str(e.children[0]), expression_to_str(e.children[1])
        ),
        "par_pattern": lambda e: "({})".format(expression_to_str(e.children[0])),
        "var_capture_pattern": lambda e: "var {}".format(
            expression_to_str(e.children[0])
        ),
        "etc_pattern": lambda _: "..",
        "wildcard_pattern": lambda _: "_",
        "array_pattern": _array_to_str,
        "dict_pattern": _dict_to_str,
        "kv_pair_pattern": lambda e: _dict_element_to_str(e.children[0]),
    }[expression.data](expression)


def _operator_chain_based_expression_to_str(expression: Tree) -> str:
    operator_expr_chain = zip(expression.children[1::2], expression.children[2::2])
    chain = [
        " {} {}".format(expression_to_str(operator), expression_to_str(expr))
        for operator, expr in operator_expr_chain
    ]
    first_expr = expression.children[0]
    return "{}{}".format(expression_to_str(first_expr), "".join(chain))


def _standalone_call_to_str(call: Tree) -> str:
    is_super_call = False
    offset = 0
    if has_leading_dot(call):
        is_super_call = True
        offset = 1

    super_prefix = "." if is_super_call else ""
    callee = expression_to_str(call.children[0 + offset])
    arguments = _arguments_to_str(call.children[1 + offset :])
    return "{}{}({})".format(super_prefix, callee, arguments)


def _getattr_call_to_str(call: Tree) -> str:
    a_getattr = expression_to_str(call.children[0])
    arguments = _arguments_to_str(call.children[1:])
    return "{}({})".format(a_getattr, arguments)


def _arguments_to_str(arguments: List[Node]) -> str:
    return ", ".join(
        [
            standalone_expression_to_str(argument)
            for argument in arguments
            if not is_any_parentheses(argument) and not is_any_comma(argument)
        ]
    )


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


def _long_string_to_str(string: Token) -> str:
    actual_string = string.value
    if actual_string.startswith("'''") and actual_string.endswith("'''"):
        fake_token = Token("REGULAR_STRING", actual_string[2:-2])
        return _regular_string_to_str(fake_token)
    return actual_string


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
