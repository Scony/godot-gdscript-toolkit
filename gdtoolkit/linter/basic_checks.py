from types import MappingProxyType
from typing import Dict, List, Set

from lark import Tree, Token

from ..common.utils import find_name_token_among_children, get_line, get_column
from ..formatter.expression_utils import remove_outer_parentheses

from .problem import Problem


def lint(parse_tree: Tree, config: MappingProxyType) -> List[Problem]:
    disable = config["disable"]
    checks_to_run_w_tree = [
        (
            "unnecessary-pass",
            _unnecessary_pass_check,
        ),
        (
            "expression-not-assigned",
            _expression_not_assigned_check,
        ),
        (
            "duplicated-load",
            _duplicated_load_check,
        ),
        (
            "unused-argument",
            _unused_argument_check,
        ),
        (
            "comparison-with-itself",
            _comparison_with_itself_check,
        ),
    ]
    problem_clusters = (
        x[1](parse_tree) if x[0] not in disable else [] for x in checks_to_run_w_tree
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
                            line=get_line(pass_stmt),
                            column=get_column(pass_stmt),
                        )
                    )
    return problems


def _expression_not_assigned_check(parse_tree: Tree) -> List[Problem]:
    problems = []
    for expr_stmt in parse_tree.find_data("expr_stmt"):
        expr = expr_stmt.children[0]
        actual_expression = remove_outer_parentheses(expr.children[0])
        if not isinstance(actual_expression, Tree) or actual_expression.data not in [
            "assnmnt_expr",
            "await_expr",
            "standalone_call",
            "getattr_call",
            "string",
        ]:
            problems.append(
                Problem(
                    name="expression-not-assigned",
                    description=(
                        "expression is not asigned, and hence it can be removed"
                    ),
                    line=get_line(actual_expression),
                    column=get_column(actual_expression),
                )
            )
    return problems


def _duplicated_load_check(parse_tree: Tree) -> List[Problem]:
    problems = []
    loaded_strings: Set[str] = set()
    for call in sorted(
        parse_tree.find_data("standalone_call"), key=lambda rule: rule.meta.line
    ):
        name_token = call.children[0]
        callee_name = name_token.value
        if (
            callee_name in ["load", "preload"]
            and len(call.children) > 1
            and isinstance(call.children[1], Tree)
            and call.children[1].data == "string"
        ):
            string_rule = call.children[1]
            loaded_string = string_rule.children[0].value
            if loaded_string in loaded_strings:
                problems.append(
                    Problem(
                        name="duplicated-load",
                        description="duplicated loading of {}".format(loaded_string),
                        line=get_line(string_rule),
                        column=get_column(string_rule),
                    )
                )
            else:
                loaded_strings.add(loaded_string)
    return problems


# pylint: disable=too-many-locals
def _unused_argument_check(parse_tree: Tree) -> List[Problem]:
    problems = []
    for func_def in parse_tree.find_data("func_def"):
        func_header = func_def.children[0]
        if (
            len(func_header.children) > 1
            and isinstance(func_header.children[1], Tree)
            and func_header.children[1].data == "func_args"
        ):
            argument_definitions = {}  # type: Dict[str, int]
            argument_tokens = {}
            func_args = func_header.children[1]
            for func_arg in func_args.children:
                arg_name_token = find_name_token_among_children(func_arg)
                arg_name = arg_name_token.value  # type: ignore
                argument_definitions[arg_name] = (
                    argument_definitions.get(arg_name, 0) + 1
                )
                argument_tokens[arg_name] = arg_name_token
            name_occurances = {}  # type: Dict[str, int]
            for xnode in func_def.iter_subtrees():
                for node in xnode.children:
                    if isinstance(node, Token) and node.type == "NAME":
                        name = node.value
                        name_occurances[name] = name_occurances.get(name, 0) + 1
            for argument, argument_definitions_number in argument_definitions.items():
                if argument_definitions_number == name_occurances[
                    argument
                ] and not argument.startswith("_"):
                    problems.append(
                        Problem(
                            name="unused-argument",
                            description="unused function argument '{}'".format(
                                argument
                            ),
                            line=get_line(argument_tokens[argument]),  # type: ignore
                            column=get_column(argument_tokens[argument]),  # type: ignore
                        )
                    )
    return problems


def _comparison_with_itself_check(parse_tree: Tree) -> List[Problem]:
    problems = []
    for comparison in parse_tree.find_data("comparison"):
        assert len(comparison.children) == 3
        if comparison.children[0] == comparison.children[2]:
            problems.append(
                Problem(
                    name="comparison-with-itself",
                    description="Redundant comparison",
                    line=get_line(comparison),
                    column=get_column(comparison),
                )
            )
    return problems


def _find_stmts_among_children(tree: Tree, suffix: str) -> List[Tree]:
    stmts = []
    for child in tree.children:
        if isinstance(child, Tree):
            name = child.data
            if name.endswith(suffix):
                stmts.append(child)
    return stmts
