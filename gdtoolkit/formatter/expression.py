from typing import List, Tuple

from lark import Tree

from .context import Context


def format_expression(
    prefix: str, expression: Tree, context: Context
) -> Tuple[List, int]:
    assert context
    formatted_lines = []
    # TODO: take original line from prefix
    formatted_lines.append(
        (expression.line, "{}{}".format(prefix, expression.children[0].value))
    )
    return (formatted_lines, expression.line)
