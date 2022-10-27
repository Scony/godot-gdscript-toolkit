from .context import Context
from .types import Tree, Node, Outcome


def format_simple_statement(
    statement_name: str, statement: Node, context: Context
) -> Outcome:
    return (
        [(statement.line, f"{context.indent_string}{statement_name}")],
        statement.line,
    )


def find_tree_among_children(tree_name_to_find: str, tree: Tree):
    for child in tree.children:
        if isinstance(child, Tree) and child.data == tree_name_to_find:
            return child
    return None
