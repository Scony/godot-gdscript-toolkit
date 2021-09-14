from functools import partial
from types import MappingProxyType
from typing import List

from lark import Tree

from .problem import Problem
from .ast import AbstractSyntaxTree
from .helpers import is_function_public


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
    checks_to_run_w_ast = [
        (
            "max-public-methods",
            partial(_max_public_methods_check, config["max-public-methods"]),
        ),
    ]
    ast = AbstractSyntaxTree(parse_tree)
    problem_clusters = map(
        lambda x: x[1](ast) if x[0] not in disable else [], checks_to_run_w_ast
    )
    problems += [problem for cluster in problem_clusters for problem in cluster]
    return problems


def _function_args_num_check(threshold, parse_tree: Tree) -> List[Problem]:
    problems = []
    for func_def in parse_tree.find_data("func_def"):
        func_header = func_def.children[0]
        func_name_token = func_header.children[0]
        assert func_name_token.type == "NAME"
        func_name = func_name_token.value
        if (
            len(func_header.children) > 1
            and isinstance(func_header.children[1], Tree)
            and func_header.children[1].data == "func_args"
        ):
            args_num = len(func_header.children[1].children)
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


def _max_public_methods_check(threshold: int, ast: AbstractSyntaxTree) -> List[Problem]:
    problems = []
    for a_class in ast.classes:
        public_functions = [f for f in a_class.functions if is_function_public(f.name)]
        if len(public_functions) > threshold:
            class_name = (
                "Class {}".format(a_class.name)
                if a_class.name is not None
                else "Global scope class"
            )
            problems.append(
                Problem(
                    name="max-public-methods",
                    description=(
                        '"{}" has more than {} public methods (functions)'.format(
                            class_name, threshold
                        )
                    ),
                    line=a_class.lark_node.line,
                    column=a_class.lark_node.column,
                )
            )
    return problems
