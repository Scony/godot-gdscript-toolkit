from typing import List, Optional

from lark import Tree

from ..common.utils import get_line, get_end_line
from .types import FormattedLine, FormattedLines, Outcome
from .context import Context, ExpressionContext
from .expression import format_concrete_expression
from .expression_to_str import expression_to_str

_STANDALONE_ANNOTATIONS = [
    "abstract",
    "export_category",
    "export_group",
    "export_subgroup",
    "icon",
    "tool",
    "warning_ignore_start",
    "warning_ignore_restore",
]

"""
Source: https://github.com/godotengine/godot/blob/master/modules/gdscript/gdscript_warning.h
Source last updated: 2025-01-09

Unused because not applicable to functions:
- "unused_variable"
- "unused_local_constant"
- "shadowed_variable"
- "shadowed_variable_base_class"
- "missing_tool"
- "empty_file"
- "unused_private_class_variable"
- "unused_signal"
- "redundant_static_unload"
- "get_node_default_without_onready"
- "onready_with_export"

Unused because deprecated:
- "property_used_as_function"
- "constant_used_as_function"
- "function_used_as_property"
"""
_NON_STANDALONE_WARNING_IGNORES = [
    # Variable used but never assigned.
    "unassigned_variable",
    # Variable never assigned but used in an assignment operation (+=, *=, etc).
    "unassigned_variable_op_assign",
    # Function parameter is never used.
    "unused_parameter",
    # A global class or function has the same name as variable.
    "shadowed_global_identifier",
    # Code after a return statement.
    "unreachable_code",
    # Pattern in a match statement after a catch all pattern (wildcard or bind).
    "unreachable_pattern",
    # Expression not assigned to a variable.
    "standalone_expression",
    # Return value of ternary expression is discarded.
    "standalone_ternary",
    # Possible values of a ternary if are not mutually compatible.
    "incompatible_ternary",
    # Variable/parameter/function has no static type, explicitly specified or implicitly inferred.
    "untyped_declaration",
    # Variable/constant/parameter has an implicitly inferred static type.
    "inferred_declaration",
    # Property not found in the detected type (but can be in subtypes).
    "unsafe_property_access",
    # Function not found in the detected type (but can be in subtypes).
    "unsafe_method_access",
    # Casting a `variant` value to non-`variant`.
    "unsafe_cast",
    # Function call argument is of a supertype of the required type.
    "unsafe_call_argument",
    # Function returns void but returned a call to a function that can't be type checked.
    "unsafe_void_return",
    # Function call returns something but the value isn't used.
    "return_value_discarded",
    # A static method was called on an instance of a class instead of on the class itself.
    "static_called_on_instance",
    # Await is used but expression is synchronous (not a signal nor a coroutine).
    "redundant_await",
    # Expression for assert argument is always true.
    "assert_always_true",
    # Expression for assert argument is always false.
    "assert_always_false",
    # Integer divide by integer, decimal part is discarded.
    "integer_division",
    # Float value into an integer slot, precision is lost.
    "narrowing_conversion",
    # An integer value was used as an enum value without casting.
    "int_as_enum_without_cast",
    # An integer value was used as an enum value without matching enum member.
    "int_as_enum_without_match",
    # A variable with an enum type does not have a default value. the default will be set to `0`
    # instead of the first enum value.
    "enum_variable_without_default",
    # The keyword is deprecated and should be replaced.
    "deprecated_keyword",
    # The identifier contains misleading characters that can be confused. e.g. "usеr"
    # (has cyrillic "е" instead of latin "e").
    "confusable_identifier",
    # The parent block declares an identifier with the same name below.
    "confusable_local_declaration",
    # The identifier will be shadowed below in the block.
    "confusable_local_usage",
    # Reassigning lambda capture does not modify the outer local variable.
    "confusable_capture_reassignment",
    # The declaration uses type inference but the value is typed as variant.
    "inference_on_variant",
    # The script method overrides a native one, this may not work as intended.
    "native_method_override",
]


def is_abstract_annotation_for_statement(statement: Tree, next_statement: Tree) -> bool:
    """Check if this is an @abstract annotation that should be combined with the next statement."""
    if statement.data != "annotation":
        return False
    name = statement.children[0].value
    if name != "abstract":
        return False
    return next_statement.data in ["abstract_func_def", "classname_stmt", "class_def"]


def is_non_standalone_annotation(statement: Tree) -> bool:
    if statement.data != "annotation":
        return False
    name = statement.children[0].value
    if name in _STANDALONE_ANNOTATIONS:
        return False
    if name != "warning_ignore":
        return True
    ignoree = statement.children[1].children[0].children[0].value.strip('"')
    if ignoree in _NON_STANDALONE_WARNING_IGNORES:
        return True
    return False


def prepend_annotations_to_formatted_line(
    line_to_prepend_to: FormattedLine, context: Context
) -> FormattedLines:
    assert len(context.annotations) > 0
    whitelineless_line = line_to_prepend_to[1].strip()
    annotations_string = " ".join(
        [format_annotation_to_string(annotation) for annotation in context.annotations]
    )
    single_line_length = (
        context.indent + len(annotations_string) + len(whitelineless_line)
    )
    # Check if this is an abstract function or class_name annotation
    is_abstract_func = (
        len(context.annotations) == 1
        and context.annotations[0].children[0].value == "abstract"
        and whitelineless_line.startswith("func")
    )
    is_abstract_class_name = (
        len(context.annotations) == 1
        and context.annotations[0].children[0].value == "abstract"
        and whitelineless_line.startswith("class_name")
    )
    standalone_formatting_enforced = (
        (
            whitelineless_line.startswith("func")
            or whitelineless_line.startswith("static func")
        )
        and not is_abstract_func
        and not is_abstract_class_name
    )
    if (
        not _annotations_have_standalone_comments(
            context.annotations, context.standalone_comments, line_to_prepend_to[0]
        )
        and single_line_length <= context.max_line_length
        and not standalone_formatting_enforced
    ):
        single_line = "{}{} {}".format(
            context.indent_string, annotations_string, whitelineless_line
        )
        context.annotations = []
        return [(line_to_prepend_to[0], single_line)]
    formatted_lines: FormattedLines = []
    for annotation in context.annotations:
        lines, _ = format_standalone_annotation(annotation, context)
        formatted_lines += lines
    formatted_lines.append(line_to_prepend_to)
    context.annotations = []
    return formatted_lines


def format_standalone_annotation(annotation: Tree, context: Context) -> Outcome:
    return format_concrete_expression(
        annotation, ExpressionContext("", get_line(annotation), "", -1), context
    )


def format_annotation_to_string(annotation: Tree) -> str:
    return expression_to_str(annotation)


def _annotations_have_standalone_comments(
    annotations: List[Tree],
    standalone_comments: List[Optional[str]],
    last_line: Optional[int],
):
    return any(
        comment is not None
        for comment in standalone_comments[
            get_line(annotations[0]) : (
                last_line if last_line is not None else get_end_line(annotations[-1])
            )
        ]
    )
