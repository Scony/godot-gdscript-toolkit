from lark import Tree

from ..common.utils import get_line, get_end_line
from .types import Outcome
from .context import Context, ExpressionContext
from .expression import format_expression


def format_const_statement(statement: Tree, context: Context) -> Outcome:
    if len(statement.children) == 4:
        prefix = f"const {statement.children[1].value} = "
    elif len(statement.children) == 5:
        prefix = f"const {statement.children[1].value} := "
    elif len(statement.children) == 6:
        prefix = (
            f"const {statement.children[1].value}: {statement.children[3].value} = "
        )
    expression_context = ExpressionContext(
        prefix, get_line(statement), "", get_end_line(statement)
    )
    return format_expression(statement.children[-1], expression_context, context)
