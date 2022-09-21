from lark import Tree

from .types import FormattedLine, FormattedLines
from .context import Context
from .expression_to_str import expression_to_str

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
    return (
        annotation.line,
        "{}{}".format(context.indent_string, format_annotation_to_string(annotation)),
    )


def format_annotation_to_string(annotation: Tree) -> str:
    return expression_to_str(annotation)
