from typing import List

from lark import Tree, Token

from .context import Context


class Enum:
    def __init__(self, enum_def: Tree):
        self.name = None
        node = enum_def.children[0].children[0]
        if isinstance(node, Token) and node.type == "NAME":
            self.name = node.value


def format_enum(enum_def: Tree, context: Context) -> (List, int):
    enum = Enum(enum_def)
    if _calculate_single_line_len(enum, context) > context.max_line_length:
        lines = _format_to_multiple_lines(enum, context)
    else:
        lines = _format_to_single_line(enum, context)
    concrete_enum_def = enum_def.children[0]
    return lines, concrete_enum_def.children[-1].line


def _calculate_single_line_len(enum: Enum, context: Context) -> int:
    return (
        context.indent
        + 4
        + 1
        + (len(enum.name) + 1 if enum.name is not None else 0)
        + 2
    )


def _format_to_single_line(enum: Enum, context: Context) -> List:
    if enum.name is not None:
        return [(-1, "{}enum {} {{}}".format(context.indent_string, enum.name))]
    return [(-1, "{}enum {{}}".format(context.indent_string))]


def _format_to_multiple_lines(enum: Enum, context: Context) -> List:
    if enum.name is not None:
        return [
            (-1, "{}enum {} {{".format(context.indent_string, enum.name)),
            (-1, "{}}}".format(context.indent_string)),
        ]
    return [(-1, "{}enum {{\n}}".format(context.indent_string))]
