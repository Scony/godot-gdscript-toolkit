from typing import List, Optional
from dataclasses import dataclass

from lark import Tree, Token

from .context import Context
from .constants import INDENT_STRING
from .types import Outcome
from .expression_to_str import standalone_expression_to_str


@dataclass
class EnumElement:
    name: str
    value: Optional[str]
    lark_node: Tree


class Enum:
    def __init__(self, enum_def: Tree):
        self.lark_node = enum_def
        self.name = self._load_name(enum_def)
        self.elements = self._load_elements(enum_def)
        self.trailing_comma = self._check_trailing_comma(enum_def)

    @staticmethod
    def _load_name(enum_def: Tree) -> Optional[str]:
        if len(enum_def.children[0].children) == 0:
            return None
        node = enum_def.children[0].children[0]
        if isinstance(node, Token) and node.type == "NAME":
            return node.value
        return None

    @staticmethod
    def _load_elements(enum_def: Tree) -> List[EnumElement]:
        elements = []
        for enum_element in enum_def.find_data("enum_element"):
            name = enum_element.children[0].value
            value = (
                standalone_expression_to_str(enum_element.children[1])
                if len(enum_element.children) > 1
                else None
            )
            elements.append(EnumElement(name=name, value=value, lark_node=enum_element))
        return elements

    @staticmethod
    def _check_trailing_comma(enum_def: Tree) -> bool:
        if len(enum_def.children[0].children) == 0:
            return False
        node = enum_def.children[0].children[-1]
        if isinstance(node, Tree) and node.data == "trailing_comma":
            return True
        return False


def format_enum(enum_def: Tree, context: Context) -> Outcome:
    enum = Enum(enum_def)
    if (
        enum.trailing_comma
        or _calculate_single_line_len(enum, context) > context.max_line_length
    ):
        lines = _format_to_multiple_lines(enum, context)
    else:
        lines = _format_to_single_line(enum, context)
    concrete_enum_def = enum_def.children[0]
    return lines, concrete_enum_def.end_line


def _calculate_single_line_len(enum: Enum, context: Context) -> int:
    keyword = 4
    space = 1
    curly_brackets = 2
    inline_comments = _calculate_total_inline_comments_len(enum, context)
    return (
        context.indent
        + keyword
        + space
        + (len(enum.name) + 1 if enum.name is not None else 0)
        + _calculate_single_line_elements_len(enum)
        + curly_brackets
        + inline_comments
    )


def _calculate_total_inline_comments_len(enum: Enum, context: Context) -> int:
    begin_line = enum.lark_node.line
    end_line = enum.lark_node.children[0].end_line
    return sum(
        len(comment) + 2
        for comment in context.inline_comments[begin_line : end_line + 1]
        if comment is not None
    )


def _calculate_single_line_elements_len(enum: Enum) -> int:
    spaces = 2 if len(enum.elements) > 0 else 0
    separators = (len(enum.elements) - 1) * 2 if len(enum.elements) > 1 else 0
    trailing_comma = 1 if enum.trailing_comma else 0
    return (
        sum(
            len(element.name)
            + (len(element.value) + 3 if element.value is not None else 0)
            for element in enum.elements
        )
        + spaces
        + separators
        + trailing_comma
    )


def _format_to_single_line(enum: Enum, context: Context) -> List:
    enum_fragments = ["{}enum ".format(context.indent_string)]
    if enum.name is not None:
        enum_fragments.append("{} ".format(enum.name))
    enum_fragments.append("{")
    enum_fragments += _format_elements_to_single_line(enum)
    enum_fragments.append("}")
    return [(enum.lark_node.line, "".join(enum_fragments))]


def _format_elements_to_single_line(enum: Enum) -> List[str]:
    fragments = []
    for i, element in enumerate(enum.elements):
        if i == 0:
            fragments.append(" {}".format(element.name))
        else:
            fragments.append(", {}".format(element.name))
        if element.value is not None:
            fragments.append(" = {}".format(element.value))
    if enum.trailing_comma:
        fragments.append(",")
    if len(enum.elements) > 0:
        fragments.append(" ")
    return fragments


def _format_to_multiple_lines(enum: Enum, context: Context) -> List:
    enum_lines = []
    line_fragments = ["{}enum ".format(context.indent_string)]
    if enum.name is not None:
        line_fragments.append("{} ".format(enum.name))
    line_fragments.append("{")
    enum_lines.append((enum.lark_node.line, "".join(line_fragments)))
    enum_lines += _format_elements_to_multiple_lines(enum, context)
    closing_brace_line = enum.lark_node.children[0].end_line
    enum_lines.append((closing_brace_line, "{}}}".format(context.indent_string)))
    return enum_lines


def _format_elements_to_multiple_lines(enum: Enum, context: Context) -> List:
    lines_w_elements = []
    for index, element in enumerate(enum.elements):
        comma = "," if enum.trailing_comma or index != len(enum.elements) - 1 else ""
        if element.value is None:
            lines_w_elements.append(
                (
                    element.lark_node.line,
                    "{}{}{}{}".format(
                        context.indent_string,
                        INDENT_STRING,
                        element.name,
                        comma,
                    ),
                )
            )
        else:
            lines_w_elements.append(
                (
                    element.lark_node.line,
                    "{}{}{} = {}{}".format(
                        context.indent_string,
                        INDENT_STRING,
                        element.name,
                        element.value,
                        comma,
                    ),
                )
            )
    return lines_w_elements
