from .context import Context, ExpressionContext
from .types import Outcome, Node
from .expression import format_expression


def format_func_statement(statement: Node, context: Context) -> Outcome:
    formatted_lines = []
    last_processed_line_no = statement.line
    if statement.data == "pass_stmt":
        formatted_lines.append((statement.line, "{}pass".format(context.indent_string)))
    elif statement.data == "func_var_stmt":
        concrete_var_stmt = statement.children[0]
        if concrete_var_stmt.data == "var_assigned":
            name = concrete_var_stmt.children[0].value
            expr = concrete_var_stmt.children[1]
            expression_context = ExpressionContext(
                "var {} = ".format(name), statement.line, ""
            )
            lines, last_processed_line_no = format_expression(
                expr, expression_context, context
            )
            formatted_lines += lines
        elif concrete_var_stmt.data == "var_empty":
            name = concrete_var_stmt.children[0].value
            formatted_lines.append(
                (statement.line, "{}var {}".format(context.indent_string, name))
            )
    elif statement.data == "expr_stmt":
        expr = statement.children[0]
        expression_context = ExpressionContext("", statement.line, "")
        lines, last_processed_line_no = format_expression(
            expr, expression_context, context
        )
        formatted_lines += lines
    elif statement.data == "return_stmt":
        if len(statement.children) == 0:
            formatted_lines.append(
                (statement.line, "{}return".format(context.indent_string))
            )
        else:
            expr = statement.children[0]
            expression_context = ExpressionContext("return ", statement.line, "")
            lines, last_processed_line_no = format_expression(
                expr, expression_context, context
            )
            formatted_lines += lines
    elif statement.data == "break_stmt":
        formatted_lines.append(
            (statement.line, "{}break".format(context.indent_string))
        )
    elif statement.data == "continue_stmt":
        formatted_lines.append(
            (statement.line, "{}continue".format(context.indent_string))
        )
    return (formatted_lines, last_processed_line_no)
