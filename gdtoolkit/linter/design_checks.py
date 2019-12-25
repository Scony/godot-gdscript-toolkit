from functools import partial
from types import MappingProxyType
from typing import List

from lark import Tree

from .. import Problem


def lint(parse_tree: Tree, config: MappingProxyType) -> List[Problem]:
    disable = config["disable"]
    checks_to_run_w_tree = [
        (
            "function-arguments-number",
            partial(_function_args_num_check, config["function-arguments-number"]),
        ),
    ]
    problem_clusters = map(
        lambda x: x[1](parse_tree) if x[0] not in disable else [], checks_to_run_w_tree
    )
    problems = [problem for cluster in problem_clusters for problem in cluster]
    return problems


def _function_args_num_check(threshold, parse_tree: Tree) -> List[Problem]:
    problems = []
    for func_def in parse_tree.find_data("func_def"):
        func_name_token = func_def.children[0]
        assert func_name_token.type == "NAME"
        func_name = func_name_token.value
        if (
            isinstance(func_def.children[1], Tree)
            and func_def.children[1].data == "func_args"
        ):
            args_num = len(func_def.children[1].children)
            if args_num > threshold:
                problems.append(
                    Problem(
                        name="function-arguments-number",
                        description='Function "{}" has more than {} arguments'.format(
                            func_name, threshold
                        ),
                        line=func_name_token.line,
                        column=func_name_token.column,
                    )
                )
    return problems
