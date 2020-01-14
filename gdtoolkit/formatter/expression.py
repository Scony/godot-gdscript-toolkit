from lark import Tree

from .context import Context
from .types import Prefix, Node, Outcome, FormattedLines


def format_expression(prefix: Prefix, expression: Tree, context: Context) -> Outcome:
    return _format_concrete_expression(prefix, expression.children[0], context)


def _format_concrete_expression(
    prefix: Prefix, expression: Node, context: Context
) -> Outcome:
    assert context
    formatted_lines = []  # type: FormattedLines
    formatted_lines.append(
        (prefix.line, "{}{}".format(prefix.string, _format_atom(expression)))
    )
    return (formatted_lines, expression.line)


def _format_atom(atom: Node) -> str:
    if isinstance(atom, Tree):
        return atom.children[0].value
    return atom.value
