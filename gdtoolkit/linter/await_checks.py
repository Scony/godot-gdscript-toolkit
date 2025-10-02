from types import MappingProxyType
from typing import List

from lark import Tree

from ..common.utils import get_line, get_column
from .problem import Problem


def lint(parse_tree: Tree, config: MappingProxyType) -> List[Problem]:
    disable = config["disable"]
    checks_to_run_w_tree = [
        (
            "missing-cancellation-check",
            _missing_cancellation_check,
        ),
    ]
    problem_clusters = (
        x[1](parse_tree) if x[0] not in disable else [] for x in checks_to_run_w_tree
    )
    problems = [problem for cluster in problem_clusters for problem in cluster]
    return problems


def _missing_cancellation_check(parse_tree: Tree) -> List[Problem]:
    """
    Check that after each await statement, there is a cancellation check.
    Expected pattern: if ct.is_cancelled() or similar
    """
    problems = []

    # Find all function definitions
    for func_def in parse_tree.find_data("func_def"):
        # Get all statements in the function body
        statements = _get_function_statements(func_def)

        # Check each await statement
        for i, stmt in enumerate(statements):
            if _contains_await(stmt):
                # Check if the next statement is a cancellation check
                if i + 1 < len(statements):
                    next_stmt = statements[i + 1]
                    if not _is_cancellation_check(next_stmt):
                        problems.append(
                            Problem(
                                name="missing-cancellation-check",
                                description="await statement not followed by cancellation check (e.g., if ct.is_cancelled())",
                                line=get_line(stmt),
                                column=get_column(stmt),
                            )
                        )
                else:
                    # await is the last statement in the function
                    problems.append(
                        Problem(
                            name="missing-cancellation-check",
                            description="await statement not followed by cancellation check (e.g., if ct.is_cancelled())",
                            line=get_line(stmt),
                            column=get_column(stmt),
                        )
                    )

    return problems


def _get_function_statements(func_def: Tree) -> List[Tree]:
    """Extract all statements from a function definition."""
    statements = []

    # Statements are direct children of func_def after func_header
    found_header = False
    for child in func_def.children:
        if isinstance(child, Tree):
            if child.data == "func_header":
                found_header = True
            elif found_header and child.data.endswith("_stmt"):
                statements.append(child)

    return statements


def _contains_await(stmt: Tree) -> bool:
    """Check if a statement contains an await expression."""
    from lark import Token
    for node in stmt.iter_subtrees():
        if isinstance(node, Tree) and node.data == "await_expr":
            # Check if it actually has await token
            for child in node.children:
                if isinstance(child, Token) and child.type == "AWAIT":
                    return True
    return False


def _is_cancellation_check(stmt: Tree) -> bool:
    """
    Check if a statement is a cancellation check.
    Looking for patterns like: if ct.is_cancelled() or if cancellation_token.is_cancelled()
    """
    from lark import Token
    if not isinstance(stmt, Tree):
        return False

    # Check if it's an if statement
    if stmt.data == "if_stmt":
        # Look for is_cancelled() call in the condition
        for node in stmt.iter_subtrees():
            if isinstance(node, Tree):
                # Check for getattr with is_cancelled
                if node.data == "getattr":
                    # getattr has children: object, dot, attribute_name
                    for child in node.children:
                        if isinstance(child, Token) and child.type == "NAME":
                            if child.value == "is_cancelled":
                                return True

    return False