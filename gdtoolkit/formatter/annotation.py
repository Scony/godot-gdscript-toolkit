from lark import Tree

from .types import FormattedLine, FormattedLines
from .context import Context

STANDALONE_ANNOTATIONS = ["tool"]


def is_non_standalone_annotation(statement: Tree) -> bool:
    if statement.data != "annotation":
        return False
    name = statement.children[0].value
    return name not in STANDALONE_ANNOTATIONS


def prepend_annotations_to_formatted_line(
    line_to_prepend_to: FormattedLine, context: Context
) -> FormattedLines:
    formatted_lines: FormattedLines = []
    for annotation in context.annotations:
        formatted_lines.append(format_annotation_to_line(annotation, context))
    formatted_lines.append(line_to_prepend_to)
    context.annotations = []
    return formatted_lines


def format_annotation_to_line(annotation: Tree, context: Context) -> FormattedLine:
    name = annotation.children[0].value
    if name == "tool":
        return (
            annotation.line,
            "{}@{}".format(
                context.indent_string,
                name,
            ),
        )
    if name == "onready":
        return (None, f"{context.indent_string}@onready")
    if name == "export_range":
        return (
            None,
            '{}@export_range(1, 100, 1, "or_greater")'.format(context.indent_string),
        )
    return (None, "")
