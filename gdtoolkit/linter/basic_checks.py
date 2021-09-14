from types import MappingProxyType
from typing import Dict, List, Set

from lark import Tree, Token

from .problem import Problem
from .helpers import find_name_token_among_children


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
            "string",
        ]:
            problems.append(
                Problem(
                    name="expression-not-assigned",
                    description=(
                        "expression is not asigned, and hence it can be removed"
                    ),
                    line=child.line,
                    column=child.column,
                )
            )
    return problems


def _duplicated_load_check(parse_tree: Tree) -> List[Problem]:
    problems = []
    loaded_strings = set()  # type: Set[str]
    for call in parse_tree.find_data("standalone_call"):
        name_token = call.children[0]
        callee_name = name_token.value
        if (
            callee_name in ["load", "preload"]
            and len(call.children) > 1
            and isinstance(call.children[2], Tree)
            and call.children[2].data == "string"
        ):
            string_rule = call.children[2]
            loaded_string = string_rule.children[0].value
            if loaded_string in loaded_strings:
                problems.append(
                    Problem(
                        name="duplicated-load",
                        description="duplicated loading of {}".format(loaded_string),
                        line=string_rule.line,
                        column=string_rule.column,
                    )
                )
            else:
                loaded_strings.add(loaded_string)
    return problems


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
                arg_name = arg_name_token.value
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
            for argument in argument_definitions:
                if argument_definitions[argument] == name_occurances[
                    argument
                ] and not argument.startswith("_"):
                    problems.append(
                        Problem(
                            name="unused-argument",
                            description="unused function argument '{}'".format(
                                argument
                            ),
                            line=argument_tokens[argument].line,
                            column=argument_tokens[argument].column,
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
                    line=comparison.line,
                    column=comparison.column,
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
