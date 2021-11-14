from typing import List, Optional

from lark import Tree

from .problem import Problem


def no_elif_return_check(parse_tree: Tree) -> List[Problem]:
    problems = []
    for if_stmt in _find_if_stmts(parse_tree):
        problems.extend(_check_elif_problems(if_stmt))
    return problems


def no_else_return_check(parse_tree: Tree) -> List[Problem]:
    problems = []
    trees_with_if_stmts = _find_trees_with_if_stmts(parse_tree)
    for tree in trees_with_if_stmts:
        var_names = _find_var_names(tree)
        for if_stmt in _find_if_stmts_among_children(tree):
            problems.extend(_check_else_problems(if_stmt, var_names))
    return problems


def _find_if_stmts(parse_tree: Tree) -> List[Tree]:
    return parse_tree.find_pred(_is_if_stmt)


def _check_elif_problems(if_stmt: Tree) -> List[Problem]:
    problems = []
    elif_branches = _find_elif_branches_to_remove(if_stmt)
    for elif_branch in elif_branches:
        problems.append(
            Problem(
                name="no-elif-return",
                description='Unnecessary "elif" after "return"',
                line=elif_branch.line,
                column=elif_branch.column,
            )
        )
    return problems


def _find_elif_branches_to_remove(if_stmt: Tree) -> List[Tree]:
    non_else_branches = _get_non_else_branches(if_stmt)
    elif_branches = _get_elif_branches(if_stmt)
    elif_branches_to_remove = []
    for i, non_else_branch in enumerate(non_else_branches[:-1]):
        if not _check_if_it_always_returns(non_else_branch):
            break
        elif_branches_to_remove.append(elif_branches[i])
    return elif_branches_to_remove


def _find_trees_with_if_stmts(parse_tree: Tree) -> List[Tree]:
    return parse_tree.find_pred(_has_if_stmt)


def _find_var_names(tree: Tree) -> List[str]:
    func_var_stmts = _find_func_var_stmts_among_children(tree)
    return list(map(_find_var_name, func_var_stmts))


def _check_else_problems(if_stmt: Tree, parent_var_names: List[str]) -> List[Problem]:
    else_branch = _find_else_branch_that_might_be_removed(if_stmt)
    if not else_branch:
        return []
    else_var_names = _find_var_names(else_branch)
    if any(else_var_name in parent_var_names for else_var_name in else_var_names):
        return []
    return [
        Problem(
            name="no-else-return",
            description='Unnecessary "else" after "return"',
            line=else_branch.line,
            column=else_branch.column,
        )
    ]


def _find_else_branch_that_might_be_removed(if_stmt: Tree) -> Optional[Tree]:
    if not _has_else_branch(if_stmt):
        return None
    non_else_branches = _get_non_else_branches(if_stmt)
    if not all(_check_if_it_always_returns(branch) for branch in non_else_branches):
        return None
    return _get_else_branch(if_stmt)


def _check_if_it_always_returns(tree: Tree) -> bool:
    if _has_return_stmt(tree):
        return True
    if _has_if_stmt_that_always_returns(tree):
        return True
    if _has_match_stmt_that_always_returns(tree):
        return True
    return False


def _check_if_if_stmt_always_returns(if_stmt: Tree) -> bool:
    if not _has_else_branch(if_stmt):
        return False
    if_stmt_branches = _get_if_stmt_branches(if_stmt)
    return all(_check_if_it_always_returns(branch) for branch in if_stmt_branches)


def _check_if_match_stmt_always_returns(match_stmt: Tree) -> bool:
    if not _has_wildcard_pattern_branch(match_stmt):
        return False
    match_stmt_branches = _get_match_stmt_branches(match_stmt)
    return all(_check_if_it_always_returns(branch) for branch in match_stmt_branches)


def _has_return_stmt(tree: Tree) -> bool:
    return len(_find_return_stmts_among_children(tree)) > 0


def _has_if_stmt(tree: Tree) -> bool:
    return len(_find_if_stmts_among_children(tree)) > 0


def _has_if_stmt_that_always_returns(tree: Tree) -> bool:
    if_stmts = _find_if_stmts_among_children(tree)
    return any(_check_if_if_stmt_always_returns(if_stmt) for if_stmt in if_stmts)


def _has_else_branch(if_stmt: Tree) -> bool:
    if_stmt_branches = _get_if_stmt_branches(if_stmt)
    return any(_is_else_branch(branch) for branch in if_stmt_branches)


def _has_match_stmt_that_always_returns(tree: Tree) -> bool:
    match_stmts = _find_match_stmts_among_children(tree)
    return any(
        _check_if_match_stmt_always_returns(match_stmt) for match_stmt in match_stmts
    )


def _has_wildcard_pattern_branch(match_stmt: List[Tree]) -> bool:
    match_stmt_branches = _get_match_stmt_branches(match_stmt)
    return any(_is_wildcard_pattern_branch(branch) for branch in match_stmt_branches)


def _find_var_name(func_var_stmt: List[Tree]) -> str:
    return func_var_stmt.children[0].children[0].value  # type: ignore


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


def _is_if_stmt(tree: Tree) -> bool:
    return tree.data == "if_stmt"


def _is_elif_branch(if_stmt_branch: Tree) -> bool:
    return if_stmt_branch.data == "elif_branch"


def _is_else_branch(if_stmt_branch: Tree) -> bool:
    return if_stmt_branch.data == "else_branch"


def _is_wildcard_pattern_branch(match_stmt_branch: Tree) -> bool:
    pattern = match_stmt_branch.children[0].children[0]
    if not isinstance(pattern, Tree):
        return False
    return pattern.data == "wildcard_pattern"


def _get_if_stmt_branches(if_stmt: Tree) -> List[Tree]:
    return if_stmt.children


def _get_match_stmt_branches(match_stmt: Tree) -> List[Tree]:
    return match_stmt.children[1:]


def _get_elif_branches(if_stmt: Tree) -> List[Tree]:
    if_stmt_branches = _get_if_stmt_branches(if_stmt)
    return [branch for branch in if_stmt_branches if _is_elif_branch(branch)]


def _get_else_branch(if_stmt: Tree) -> Tree:
    if_stmt_branches = _get_if_stmt_branches(if_stmt)
    return next(branch for branch in if_stmt_branches if _is_else_branch(branch))


def _get_non_else_branches(if_stmt: Tree) -> List[Tree]:
    if_stmt_branches = _get_if_stmt_branches(if_stmt)
    return [branch for branch in if_stmt_branches if not _is_else_branch(branch)]
