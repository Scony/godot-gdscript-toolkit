from lark import Tree

from .types import Node
from .expression_utils import is_any_comma


def expression_to_str(expression: Node) -> str:
    if isinstance(expression, Tree):
        return {
            "subscr_expr": _subscription_to_str,
            "array": _array_to_str,
            "dict": _dict_to_str,
            "c_dict_element": _dict_element_to_str,
            "eq_dict_element": _dict_element_to_str,
            "string": lambda e: e.children[0].value,
            "node_path": lambda e: "@{}".format(expression_to_str(e.children[0])),
            "get_node": lambda e: "${}".format(expression_to_str(e.children[0])),
            "path": lambda e: "/".join([name_token.value for name_token in e.children]),
        }[expression.data](expression)
    return expression.value


def _array_to_str(array: Tree) -> str:
    elements = [
        expression_to_str(child) for child in array.children if not is_any_comma(child)
    ]
    return "[{}]".format(", ".join(elements))


def _dict_to_str(a_dict: Tree) -> str:
    elements = [expression_to_str(child) for child in a_dict.children]
    return "{{{}}}".format(", ".join(elements))


def _subscription_to_str(subscription: Tree) -> str:
    return "{}[{}]".format(
        expression_to_str(subscription.children[0]),
        expression_to_str(subscription.children[1]),
    )


def _dict_element_to_str(dict_element: Tree) -> str:
    template = "{}: {}" if dict_element.data == "c_dict_element" else "{} = {}"
    return template.format(
        expression_to_str(dict_element.children[0]),
        expression_to_str(dict_element.children[1]),
    )
