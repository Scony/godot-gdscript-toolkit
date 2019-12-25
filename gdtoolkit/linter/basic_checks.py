from types import MappingProxyType
from typing import List

from lark import Tree

from .. import Problem


def lint(parse_tree: Tree, config: MappingProxyType) -> List[Problem]:
    disable = config["disable"]
    checks_to_run_w_tree = [
        ("unnecessary-pass", _unnecessary_pass_check,),
        ("expression-not-assigned", _expression_not_assigned_check,),
    ]
    problem_clusters = map(
        lambda x: x[1](parse_tree) if x[0] not in disable else [], checks_to_run_w_tree
    )
    problems = [problem for cluster in problem_clusters for problem in cluster]
    return problems


def _unnecessary_pass_check(parse_tree: Tree) -> List[Problem]:
    problems = []
    for node in parse_tree.iter_subtrees():
        if isinstance(node, Tree):
            pass_stmts = _find_stmts_among_children(tree=node, suffix="pass_stmt")
            all_stmts = _find_stmts_among_children(tree=node, suffix="_stmt")
            if len(pass_stmts) < len(all_stmts):
                for pass_stmt in pass_stmts:
                    problems.append(
                        Problem(
                            name="unnecessary-pass",
                            description='"pass" statement not necessary',
                            line=pass_stmt.line,
                            column=pass_stmt.column,
                        )
                    )
    return problems


def _expression_not_assigned_check(parse_tree: Tree) -> List[Problem]:
    problems = []
    for expr_stmt in parse_tree.find_data("expr_stmt"):
        expr = expr_stmt.children[0]
        child = expr.children[0]
        if not isinstance(child, Tree) or child.data not in [
            "assnmnt_expr",
            "standalone_call",
            "getattr_call",
        ]:
            problems.append(
                Problem(
                    name="expression-not-assigned",
                    description="expression is not asigned, and hence it can be removed",
                    line=child.line,
                    column=child.column,
                )
            )
    return problems


def _find_stmts_among_children(tree: Tree, suffix: str):
    stmts = []
    for child in tree.children:
        if isinstance(child, Tree):
            name = child.data
            if name.endswith(suffix):
                stmts.append(child)
    return stmts
