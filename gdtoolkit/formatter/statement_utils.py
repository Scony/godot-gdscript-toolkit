from .context import Context
from .types import Node, Outcome


def format_simple_statement(
    statement_name: str, statement: Node, context: Context
) -> Outcome:
    return (
        [(statement.line, "{}{}".format(context.indent_string, statement_name))],
        statement.line,
    )
