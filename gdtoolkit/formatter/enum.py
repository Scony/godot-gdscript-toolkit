from typing import List, Union

from lark import Tree, Token

from .context import Context


# TODO: turn methods into functions
class Enum:
    def __init__(self, enum_def: Tree):
        self.lark_node = enum_def
        self.name = self._load_name(enum_def)
        self.elements = []
        self.trailing_comma = self._check_trailing_comma(enum_def)
        self._load_elements()

    # pylint: disable=no-self-use
    def _load_name(self, enum_def: Tree) -> Union[str, None]:
        node = enum_def.children[0].children[0]
        if isinstance(node, Token) and node.type == "NAME":
            return node.value
        return None

    def _load_elements(self):
        for enum_element in self.lark_node.find_data("enum_element"):
            name = enum_element.children[0].value
            value = (
                enum_element.children[1].value
                if len(enum_element.children) > 1
                else None
            )
            self.elements.append((name, value))

    # pylint: disable=no-self-use
    def _check_trailing_comma(self, enum_def: Tree) -> bool:
        node = enum_def.children[0].children[-2]
        if isinstance(node, Token) and node.type == "COMMA":
            return True
        return False


def format_enum(enum_def: Tree, context: Context) -> (List, int):
    enum = Enum(enum_def)
    if (
        enum.trailing_comma
        or _calculate_single_line_len(enum, context) > context.max_line_length
    ):
        lines = _format_to_multiple_lines(enum, context)
    else:
        lines = _format_to_single_line(enum, context)
    concrete_enum_def = enum_def.children[0]
    return lines, concrete_enum_def.children[-1].line


# TODO: name magic numbers
def _calculate_single_line_len(enum: Enum, context: Context) -> int:
    return (
        context.indent
        + 4
        + 1
        + (len(enum.name) + 1 if enum.name is not None else 0)
        + _calculate_single_line_elements_len(enum)
        + 2
    )


def _calculate_single_line_elements_len(enum: Enum) -> int:
    spaces = 2 if len(enum.elements) > 0 else 0
    separators = (len(enum.elements) - 1) * 2 if len(enum.elements) > 1 else 0
    return (
        sum(
            [
                len(name) + (len(str(value)) + 3 if value is not None else 0)
                for name, value in enum.elements
            ]
        )
        + spaces
        + separators
    )


def _format_to_single_line(enum: Enum, context: Context) -> List:
    enum_fragments = ["{}enum ".format(context.indent_string)]
    if enum.name is not None:
        enum_fragments.append("{} ".format(enum.name))
    enum_fragments.append("{")
    enum_fragments += _format_elements_to_single_line(enum)
    enum_fragments.append("}")
    return [(-1, "".join(enum_fragments))]


def _format_elements_to_single_line(enum: Enum) -> List[str]:
    fragments = []
    for i, element in enumerate(enum.elements):
        if i == 0:
            fragments.append(" {}".format(element[0]))
        else:
            fragments.append(", {}".format(element[0]))
        if element[1] is not None:
            fragments.append(" = {}".format(element[1]))
    if len(enum.elements) > 0:
        fragments.append(" ")
    return fragments


def _format_to_multiple_lines(enum: Enum, context: Context) -> List:
    enum_lines = []
    line_fragments = ["{}enum ".format(context.indent_string)]
    if enum.name is not None:
        line_fragments.append("{} ".format(enum.name))
    line_fragments.append("{")
    enum_lines.append((-1, "".join(line_fragments)))
    enum_lines += _format_elements_to_multiple_lines(enum, context)
    enum_lines.append((-1, "{}}}".format(context.indent_string)))
    return enum_lines


# TODO: take 4 spaces from context
def _format_elements_to_multiple_lines(enum: Enum, context: Context) -> List:
    lines_w_elements = []
    for name, value in enum.elements:
        if value is None:
            lines_w_elements.append(
                (-1, "{}    {},".format(context.indent_string, name))
            )
        else:
            lines_w_elements.append(
                (-1, "{}    {} = {},".format(context.indent_string, name, value))
            )
    return lines_w_elements
