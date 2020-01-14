from typing import List, Tuple

from lark import Tree

from .context import Context
from .types import Prefix, Node


def format_expression(
    prefix: Prefix, expression: Tree, context: Context
) -> Tuple[List, int]:
    return _format_concrete_expression(prefix, expression.children[0], context)


def _format_concrete_expression(
    prefix: Prefix, expression: Node, context: Context
) -> Tuple[List, int]:
    assert context
    formatted_lines = []
    formatted_lines.append(
        (prefix.line, "{}{}".format(prefix.string, _format_atom(expression)))
    )
    return (formatted_lines, expression.line)


def _format_atom(atom: Node) -> str:
    if isinstance(atom, Tree):
        return atom.children[0].value
    return atom.value
