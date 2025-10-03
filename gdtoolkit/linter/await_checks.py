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
        (
            "missing-cancellation-token-argument",
            _missing_cancellation_token_argument,
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

    # Check if the file has a file-level warning_ignore annotation
    if _has_file_level_ignore(parse_tree, "missing_cancellation_check"):
        # Skip all checks in this file
        return problems

    # Check each class separately for class-level ignores
    for class_def in parse_tree.find_data("class_def"):
        if _has_class_ignore(class_def, "missing_cancellation_check"):
            # Skip all functions in this class
            continue

        # Process functions in this class
        for func_def in class_def.find_data("func_def"):
            _check_function_cancellation(func_def, problems)

    # Also check top-level functions (not in any class)
    _check_top_level_functions(parse_tree, problems)

    return problems


def _check_function_cancellation(func_def: Tree, problems: List[Problem]) -> None:
    """Check a single function for missing cancellation checks."""
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


def _missing_cancellation_token_argument(parse_tree: Tree) -> List[Problem]:
    """
    Check that when calling async methods (with await), cancellation token is passed.
    Expected pattern: await some_method(ct) or await some_method(arg1, ct)
    """
    from lark import Token
    problems = []

    # Find all function definitions
    for func_def in parse_tree.find_data("func_def"):
        # Get cancellation token parameter names from function signature
        ct_params = _get_cancellation_token_params(func_def)

        if not ct_params:
            # Function doesn't have cancellation token parameter, skip
            continue

        # Find all await expressions in the function
        for await_expr in func_def.find_data("await_expr"):
            # Check if it's a method call
            call_node = None
            for child in await_expr.children:
                if isinstance(child, Tree) and child.data in ["standalone_call", "getattr_call"]:
                    call_node = child
                    break

            if call_node is None:
                continue

            # Check if cancellation token is passed as argument
            has_ct_argument = _has_cancellation_token_argument(call_node, ct_params)

            if not has_ct_argument:
                problems.append(
                    Problem(
                        name="missing-cancellation-token-argument",
                        description="async method call should pass cancellation token (e.g., await method(ct))",
                        line=get_line(await_expr),
                        column=get_column(await_expr),
                    )
                )

    return problems


def _get_cancellation_token_params(func_def: Tree) -> set:
    """
    Extract cancellation token parameter names from function definition.
    Looks for parameters named 'ct', 'cancellation_token', or containing 'token'.
    """
    from lark import Token
    ct_params = set()

    # Find func_args in func_header
    for child in func_def.children:
        if isinstance(child, Tree) and child.data == "func_header":
            for header_child in child.children:
                if isinstance(header_child, Tree) and header_child.data == "func_args":
                    # Iterate through function arguments
                    for arg in header_child.children:
                        if isinstance(arg, Tree) and arg.data in ["func_arg_regular", "func_arg_typed"]:
                            # Get the argument name (first NAME token)
                            for arg_child in arg.children:
                                if isinstance(arg_child, Token) and arg_child.type == "NAME":
                                    param_name = arg_child.value
                                    # Check if it looks like a cancellation token
                                    if _is_cancellation_token_name(param_name):
                                        ct_params.add(param_name)
                                    break  # Only get the first NAME (parameter name, not type)

    return ct_params


def _is_cancellation_token_name(name: str) -> bool:
    """Check if a parameter name looks like a cancellation token."""
    name_lower = name.lower()
    return (
        name_lower == "ct" or
        name_lower == "cancellation_token" or
        "token" in name_lower or
        name_lower == "cancel_token"
    )


def _has_cancellation_token_argument(call_node: Tree, ct_params: set) -> bool:
    """
    Check if a method call passes any of the cancellation token parameters.
    """
    from lark import Token

    # Get all arguments passed to the call
    for child in call_node.children:
        if isinstance(child, Token) and child.type == "NAME":
            # Check if this argument is one of the ct parameters
            if child.value in ct_params:
                return True

    return False


def _has_class_ignore(class_def: Tree, check_name: str) -> bool:
    """
    Check if a class has a @warning_ignore annotation for the given check.
    """
    from lark import Token

    # Look for annotations in the class definition
    for child in class_def.children:
        if isinstance(child, Tree) and child.data == "annotation":
            # Check if it's a warning_ignore annotation
            annotation_name = None
            annotation_args = []

            for ann_child in child.children:
                if isinstance(ann_child, Token) and ann_child.type == "NAME":
                    annotation_name = ann_child.value
                elif isinstance(ann_child, Tree) and ann_child.data == "annotation_args":
                    # Extract string arguments
                    for arg in ann_child.iter_subtrees():
                        if arg.data == "string":
                            for token in arg.children:
                                if isinstance(token, Token) and token.type == "STRING":
                                    # Remove quotes from string
                                    arg_value = token.value.strip('"\'')
                                    annotation_args.append(arg_value)

            if annotation_name == "warning_ignore" and check_name in annotation_args:
                return True

    return False


def _check_top_level_functions(parse_tree: Tree, problems: List[Problem]) -> None:
    """
    Check top-level functions (not in any class) for missing cancellation checks.
    """
    # Collect all class_def nodes
    class_defs = set(parse_tree.find_data("class_def"))

    # Find all function definitions
    for func_def in parse_tree.find_data("func_def"):
        # Check if this func_def is inside any class
        is_in_class = False
        for class_def in class_defs:
            # Check if func_def is a descendant of this class_def
            if _is_descendant(class_def, func_def):
                is_in_class = True
                break

        if not is_in_class:
            # This is a top-level function
            _check_function_cancellation(func_def, problems)


def _is_descendant(parent: Tree, potential_child: Tree) -> bool:
    """
    Check if potential_child is a descendant of parent in the tree.
    """
    for node in parent.iter_subtrees():
        if node is potential_child:
            return True
    return False


def _has_file_level_ignore(parse_tree: Tree, check_name: str) -> bool:
    """
    Check if the file has a file-level @warning_ignore annotation.
    This is for files that use class_name at the top level.
    """
    from lark import Token

    # In GDScript, when using class_name, annotations appear as direct children of start
    # Look for annotation nodes in the parse tree root
    for child in parse_tree.children:
        if isinstance(child, Tree) and child.data == "annotation":
            # Check if it's a warning_ignore annotation
            annotation_name = None
            annotation_args = []

            for ann_child in child.children:
                if isinstance(ann_child, Token) and ann_child.type == "NAME":
                    annotation_name = ann_child.value
                elif isinstance(ann_child, Tree) and ann_child.data == "annotation_args":
                    # Extract string arguments
                    for arg in ann_child.iter_subtrees():
                        if arg.data == "string":
                            for token in arg.children:
                                if isinstance(token, Token) and token.type == "STRING":
                                    # Remove quotes from string
                                    arg_value = token.value.strip('"\'')
                                    annotation_args.append(arg_value)

            if annotation_name == "warning_ignore" and check_name in annotation_args:
                return True

    return False