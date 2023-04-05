from functools import partial
from types import MappingProxyType
from typing import List

from lark import Tree

from ..common.utils import get_line, get_column
from ..common.ast import AbstractSyntaxTree

from .problem import Problem
from .helpers import is_function_public


def lint(parse_tree: Tree, config: MappingProxyType) -> List[Problem]:
    disable = config["disable"]
    checks_to_run_w_ast = [
        (
            "max-public-methods",
            partial(_max_public_methods_check, config["max-public-methods"]),
        ),
        (
            "max-returns",
            partial(_max_returns_check, config["max-returns"]),
        ),
        (
            "function-arguments-number",
            partial(_function_args_num_check, config["function-arguments-number"]),
        ),
    ]
    ast = AbstractSyntaxTree(parse_tree)
    problem_clusters = (
        x[1](ast) if x[0] not in disable else [] for x in checks_to_run_w_ast
    )
    problems = [problem for cluster in problem_clusters for problem in cluster]
    return problems


def _function_args_num_check(threshold: int, ast: AbstractSyntaxTree) -> List[Problem]:
    problems = []
    for function in ast.all_functions:
        if len(function.parameters) > threshold:
            problems.append(
                Problem(
                    name="function-arguments-number",
                    description='Function "{}" has more than {} arguments'.format(
                        function.name, threshold
                    ),
                    line=get_line(function.lark_node),
                    column=get_column(function.lark_node),
                )
            )
    return problems


def _max_public_methods_check(threshold: int, ast: AbstractSyntaxTree) -> List[Problem]:
    problems = []
    for a_class in ast.all_classes:
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
                    line=get_line(a_class.lark_node),
                    column=get_column(a_class.lark_node),
                )
            )
    return problems


def _max_returns_check(threshold: int, ast: AbstractSyntaxTree) -> List[Problem]:
    problems = []
    for function in ast.all_functions:
        returns = [
            statement
            for statement in function.all_statements
            if statement.kind == "return_stmt"
        ]
        if len(returns) > threshold:
            problems.append(
                Problem(
                    name="max-returns",
                    description='Function "{}" has more than {} return statements'.format(
                        function.name, threshold
                    ),
                    line=get_line(returns[-1].lark_node),
                    column=get_column(returns[-1].lark_node),
                )
            )
    return problems
