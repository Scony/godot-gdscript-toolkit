from lark import Tree

from .types import Node
from .expression_utils import is_foldable


def expression_to_str(expression: Node) -> str:
    if is_foldable(expression):
        return foldable_to_str(expression)
    return non_foldable_to_str(expression)


def foldable_to_str(expression: Node) -> str:
    if expression.data == "array":
        array_elements = [
            expression_to_str(child)
            for child in expression.children
            if isinstance(child, Tree) or child.type != "COMMA"
        ]
        return "[{}]".format(", ".join(array_elements))
    if expression.data == "dict":
        elements = [_dict_element_to_str(child) for child in expression.children]
        return "{{{}}}".format(", ".join(elements))
    if expression.data == "subscr_expr":
        return "{}[{}]".format(
            expression_to_str(expression.children[0]),
            expression_to_str(expression.children[1]),
        )
    return ""


def non_foldable_to_str(expression: Node) -> str:
    if isinstance(expression, Tree):
        if expression.data == "string":
            return expression.children[0].value
        if expression.data == "node_path":
            return "{}{}".format("@", non_foldable_to_str(expression.children[0]))
        if expression.data == "get_node":
            return "{}{}".format("$", non_foldable_to_str(expression.children[0]))
        if expression.data == "path":
            return "/".join([name_token.value for name_token in expression.children])
    return expression.value


def _dict_element_to_str(dict_element: Tree) -> str:
    template = "{}: {}" if dict_element.data == "c_dict_element" else "{} = {}"
    return template.format(
        expression_to_str(dict_element.children[0]),
        expression_to_str(dict_element.children[1]),
    )
