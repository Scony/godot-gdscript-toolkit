from ..common.utils import get_line
from ..common.types import Node
from .context import Context
from .types import Outcome


def format_simple_statement(
    statement_name: str, statement: Node, context: Context
) -> Outcome:
    return (
        [(get_line(statement), f"{context.indent_string}{statement_name}")],
        get_line(statement),
    )
