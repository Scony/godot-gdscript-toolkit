from .types import Outcome, Node
from .context import Context
from .block import format_block
from .function_statement import format_func_statement
from .enum import format_enum


def format_class_statement(statement: Node, context: Context) -> Outcome:
    formatted_lines = []
    last_processed_line_no = statement.line
    if statement.data == "tool_stmt":
        formatted_lines.append((statement.line, "{}tool".format(context.indent_string)))
    elif statement.data == "class_var_stmt":
        concrete_var_stmt = statement.children[0]
        if concrete_var_stmt.data == "var_empty":
            name = concrete_var_stmt.children[0].value
            formatted_lines.append(
                (statement.line, "{}var {}".format(context.indent_string, name))
            )
    elif statement.data == "extends_stmt":
        formatted_lines.append(
            (
                statement.line,
                "{}extends {}".format(
                    context.indent_string, statement.children[0].value
                ),
            )
        )
    elif statement.data == "class_def":
        name = statement.children[0].value
        formatted_lines.append(
            (statement.line, "{}class {}:".format(context.indent_string, name))
        )
        class_lines, last_processed_line_no = format_block(
            statement.children[1:],
            format_class_statement,
            context.create_child_context(last_processed_line_no),
        )
        formatted_lines += class_lines
    elif statement.data == "func_def":
        name = statement.children[0].value
        formatted_lines.append(
            (statement.line, "{}func {}():".format(context.indent_string, name))
        )
        func_lines, last_processed_line_no = format_block(
            statement.children[1:],
            format_func_statement,
            context.create_child_context(last_processed_line_no),
        )
        formatted_lines += func_lines
    elif statement.data == "enum_def":
        enum_lines, last_processed_line_no = format_enum(statement, context)
        formatted_lines += enum_lines
    return (formatted_lines, last_processed_line_no)
