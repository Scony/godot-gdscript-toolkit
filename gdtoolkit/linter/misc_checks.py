from types import MappingProxyType
from typing import List

from lark import Tree

from .problem import Problem
from .if_return_checks import no_elif_return_check, no_else_return_check


def lint(parse_tree: Tree, config: MappingProxyType) -> List[Problem]:
    disable = config["disable"]
    checks_to_run_w_tree = [
        (
            "no-elif-return",
            no_elif_return_check,
        ),
        (
            "no-else-return",
            no_else_return_check,
        ),
    ]
    problem_clusters = map(
        lambda x: x[1](parse_tree) if x[0] not in disable else [], checks_to_run_w_tree
    )
    problems = [problem for cluster in problem_clusters for problem in cluster]
    return problems
