from lark import Tree
from lark.tree import Meta

from .statement_utils import find_tree_among_children
from .types import FormattedLine, FormattedLines, Outcome
from .context import Context
from .block import format_block


def has_inline_property_body(statement: Tree) -> bool:
    return find_tree_among_children("inline_property_body", statement)


def append_property_body_to_formatted_line(
    line_to_append_to: FormattedLine, inline_property_body: Tree, context: Context
) -> FormattedLines:
    formatted_lines = [(line_to_append_to[0], f"{line_to_append_to[1]}:")]
    property_delegates = inline_property_body.children
    if len(property_delegates) > 0:
        fake_meta = Meta()
        fake_meta.line = inline_property_body.children[0].line
        fake_property_body = Tree(
            "property_body", inline_property_body.children, fake_meta
        )
        extra_lines, _ = format_property_body(fake_property_body, context)
        formatted_lines += extra_lines
    return formatted_lines


def format_property_body(property_body: Tree, context: Context) -> Outcome:
    formatted_lines, last_processed_line = format_block(
        property_body.children,
        _format_property_statement,
        context.create_child_context(property_body.line),
    )
    if (
        property_body.children[0].data.startswith("property_delegate")
        and len(property_body.children) > 1
    ):
        for formatted_line_index, formatted_line in enumerate(formatted_lines):
            if formatted_line[0] == property_body.children[0].line:
                formatted_lines[formatted_line_index] = (
                    formatted_line[0],
                    formatted_line[1] + ",",
                )
                break
    return (formatted_lines, last_processed_line)


def _format_property_statement(statement: Tree, context: Context) -> Outcome:
    handlers = {
        "property_delegate_set": _format_property_delegate,
        "property_delegate_get": _format_property_delegate,
        "property_custom_getter": _format_property_etter,
    }
    return handlers[statement.data](statement, context)


def _format_property_etter(property_etter: Tree, context: Context) -> Outcome:
    child_context = context.create_child_context(property_etter.line)
    return (
        [
            (property_etter.line, f"{context.indent_string}get:"),
            (property_etter.line, f"{child_context.indent_string}pass"),
        ],
        property_etter.line,
    )


def _format_property_delegate(property_delegate: Tree, context: Context) -> Outcome:
    return (
        [
            (
                property_delegate.line,
                "{}{} = {}".format(
                    context.indent_string,
                    property_delegate.children[0].value,
                    property_delegate.children[2].value,
                ),
            )
        ],
        property_delegate.line,
    )
