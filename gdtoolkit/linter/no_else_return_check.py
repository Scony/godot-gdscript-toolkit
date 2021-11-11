from typing import List, Optional

from lark import Tree

from .problem import Problem

def no_else_return_check(options, parse_tree: Tree) -> List[Problem]:
    problems = []
    allow_elif = options["allow-elif"]
    trees_with_if_stmts = _find_trees_with_if_stmts(parse_tree)
    for tree in trees_with_if_stmts:
        var_names = _find_var_names(tree)
        for if_stmt in _find_if_stmts_among_children(tree):
            if not allow_elif:
                problems.extend(_check_elif_problems(if_stmt))
            problems.extend(_check_else_problems(if_stmt, var_names, allow_elif))
    return problems


def _find_trees_with_if_stmts(parse_tree: Tree) -> List[Tree]:
    return parse_tree.find_pred(_has_if_stmt)


def _find_var_names(tree: Tree) -> List[str]:
    func_var_stmts = _find_func_var_stmts_among_children(tree)
    return map(_find_var_name, func_var_stmts)


def _check_elif_problems(if_stmt: Tree) -> List[Problem]:
    elif_problems = []
    for elif_branch in _find_elif_branches_to_remove(if_stmt):
        elif_problems.append(
            Problem(
                name="no-else-return",
                description="Unnecessary \"elif\" after \"return\"",
                line=elif_branch.line,
                column=elif_branch.column,
            )
        )
    return elif_problems


def _check_else_problems(
    if_stmt: Tree, parent_var_names: List[str], allow_elif: bool
) -> List[Problem]:
    else_branch = _find_else_branch_that_might_be_removed(if_stmt, allow_elif)
    if not else_branch:
        return []
    else_var_names = _find_var_names(else_branch)
    if any(else_var_name in parent_var_names for else_var_name in else_var_names):
        return []
    return [
        Problem(
            name="no-else-return",
            description="Unnecessary \"else\" after \"return\"",
            line=else_branch.line,
            column=else_branch.column,
        )
    ]


def _find_elif_branches_to_remove(if_stmt: Tree) -> List[Tree]:
    branches = _find_if_stmt_branches(if_stmt)
    if_branch = _find_if_branch(branches)
    if not _check_if_it_always_returns(if_branch):
        return []
    return _find_elif_branches(branches)


def _find_else_branch_that_might_be_removed(
    if_stmt: Tree, allow_elif: bool
) -> Optional[Tree]:
    branches = _find_if_stmt_branches(if_stmt)
    if not _has_else_branch(branches):
        return None
    branches_to_check = _find_branches_to_check(branches, allow_elif)
    if not all(_check_if_it_always_returns(branch) for branch in branches_to_check):
        return None
    return _find_else_branch(branches)


def _find_branches_to_check(
    if_stmt_branches: List[Tree], allow_elif: bool
) -> List[Tree]:
    if allow_elif:
        return _find_non_else_branches(if_stmt_branches)
    return [_find_if_branch(if_stmt_branches)]


def _check_if_it_always_returns(tree: Tree) -> bool:
    if _has_return_stmt(tree):
        return True
    if _has_if_stmt_that_always_returns(tree):
        return True
    if _has_match_stmt_that_always_returns(tree):
        return True
    return False


def _has_return_stmt(tree: Tree) -> bool:
    return len(_find_return_stmts_among_children(tree)) > 0


def _has_if_stmt_that_always_returns(tree: Tree) -> bool:
    if_stmts = _find_if_stmts_among_children(tree)
    return any(_check_if_if_stmt_always_returns(if_stmt) for if_stmt in if_stmts)


def _check_if_if_stmt_always_returns(if_stmt: Tree) -> bool:
    branches = _find_if_stmt_branches(if_stmt)
    if not _has_else_branch(branches):
        return False
    return all(_check_if_it_always_returns(branch) for branch in branches)


def _has_match_stmt_that_always_returns(tree: Tree) -> bool:
    match_stmts = _find_match_stmts_among_children(tree)
    return any(
        _check_if_match_stmt_always_returns(match_stmt) for match_stmt in match_stmts
    )


def _check_if_match_stmt_always_returns(match_stmt: Tree) -> bool:
    branches = _find_match_stmt_branches(match_stmt)
    if not _has_wildcard_pattern_branch(branches):
        return False
    return all(_check_if_it_always_returns(branch) for branch in branches)


def _find_if_stmt_branches(if_stmt: Tree) -> List[Tree]:
    return if_stmt.children


def _find_match_stmt_branches(match_stmt: Tree) -> List[Tree]:
    return match_stmt.children[1:]


def _find_var_name(func_var_stmt: List[Tree]) -> str:
    return func_var_stmt.children[0].children[0].value


def _find_if_branch(if_stmt_branches: List[Tree]) -> Tree:
    return next(branch for branch in if_stmt_branches if _is_if_branch(branch))


def _find_elif_branches(if_stmt_branches: List[Tree]) -> List[Tree]:
    return [branch for branch in if_stmt_branches if _is_elif_branch(branch)]


def _find_else_branch(if_stmt_branches: List[Tree]) -> Tree:
    return next(branch for branch in if_stmt_branches if _is_else_branch(branch))


def _find_non_else_branches(if_stmt_branches: List[Tree]) -> List[Tree]:
    return [branch for branch in if_stmt_branches if not _is_else_branch(branch)]


def _has_if_stmt(tree: Tree) -> bool:
    return len(_find_if_stmts_among_children(tree)) > 0


def _has_else_branch(if_stmt_branches: List[Tree]) -> bool:
    return any(_is_else_branch(branch) for branch in if_stmt_branches)


def _has_wildcard_pattern_branch(match_stmt_branches: List[Tree]) -> bool:
    return any(_is_wildcard_pattern_branch(branch) for branch in match_stmt_branches)


def _find_func_var_stmts_among_children(tree: Tree) -> List[Tree]:
    return _find_stmts_among_children(tree=tree, suffix="func_var_stmt")


def _find_if_stmts_among_children(tree: Tree) -> List[Tree]:
    return _find_stmts_among_children(tree=tree, suffix="if_stmt")


def _find_match_stmts_among_children(tree: Tree) -> List[Tree]:
    return _find_stmts_among_children(tree=tree, suffix="match_stmt")


def _find_return_stmts_among_children(tree: Tree) -> List[Tree]:
    return _find_stmts_among_children(tree=tree, suffix="return_stmt")


def _find_stmts_among_children(tree: Tree, suffix: str) -> List[Tree]:
    stmts = []
    for child in tree.children:
        if isinstance(child, Tree):
            name = child.data
            if name.endswith(suffix):
                stmts.append(child)
    return stmts


def _is_if_branch(if_stmt_branch: Tree) -> bool:
    return if_stmt_branch.data == "if_branch"


def _is_elif_branch(if_stmt_branch: Tree) -> bool:
    return if_stmt_branch.data == "elif_branch"


def _is_else_branch(if_stmt_branch: Tree) -> bool:
    return if_stmt_branch.data == "else_branch"


def _is_wildcard_pattern_branch(match_stmt_branch: Tree) -> bool:
    pattern = match_stmt_branch.children[0].children[0]
    if not isinstance(pattern, Tree):
        return False
    return pattern.data == "wildcard_pattern"
