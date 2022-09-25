from typing import List

from lark import Tree

from .statement_utils import find_tree_among_children
from .types import FormattedLine, FormattedLines, Outcome
from .context import Context


def has_inline_property_body(statement: Tree) -> bool:
    return find_tree_among_children("inline_property_body", statement)


def append_property_body_to_formatted_line(
    line_to_append_to: FormattedLine, inline_property_body: Tree, context: Context
) -> FormattedLines:
    formatted_lines = [(line_to_append_to[0], f"{line_to_append_to[1]}:")]
    child_context = context.create_child_context(inline_property_body.line)
    formatted_lines += _format_property_delegates(
        inline_property_body.children, child_context
    )
    return formatted_lines


def format_property_body(property_body: Tree, context: Context) -> Outcome:
    assert property_body.children[0].data.startswith("property_delegate")
    formatted_lines = _format_property_delegates(
        property_body.children, context.create_child_context(property_body.line)
    )
    # TODO: fix return type
    return (formatted_lines, formatted_lines[-1][0])  # type: ignore


def _format_property_delegates(
    property_delegates: List[Tree], context: Context
) -> FormattedLines:
    formatted_lines = [
        _format_property_delegate(
            property_delegate,
            context,
        )
        for property_delegate in property_delegates
    ]
    if len(formatted_lines) == 2:
        formatted_lines = [
            (
                formatted_lines[0][0],
                f"{formatted_lines[0][1]},",
            ),
            formatted_lines[1],
        ]
    return formatted_lines


def _format_property_delegate(
    property_delegate: Tree, context: Context
) -> FormattedLine:
    return (
        property_delegate.line,
        "{}{} = {}".format(
            context.indent_string,
            property_delegate.children[0].value,
            property_delegate.children[2].value,
        ),
    )
