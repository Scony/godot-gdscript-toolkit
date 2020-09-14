import re
from functools import partial
from typing import Dict, List
from types import MappingProxyType

from lark import Tree

from .problem import Problem
from .helpers import find_name_token_among_children


def lint(parse_tree: Tree, config: MappingProxyType) -> List[Problem]:
    disable = config["disable"]
    rule_name_tokens = _gather_rule_name_tokens(
        parse_tree,
        [
            "class_def",
            "func_def",
            "classname_stmt",
            "signal_stmt",
            "enum_named",
            "enum_element",
            "for_stmt",
            "func_arg_regular",
            "func_arg_inf",
            "func_arg_typed",
        ],
    )
    checks_to_run_wo_tree = [
        (
            "function-name",
            partial(
                _generic_name_check,
                config["function-name"],
                rule_name_tokens["func_def"],
                "function-name",
                'Function name "{}" is not valid',
            ),
        ),
        (
            "sub-class-name",
            partial(
                _generic_name_check,
                config["sub-class-name"],
                rule_name_tokens["class_def"],
                "sub-class-name",
                'Class name "{}" is not valid',
            ),
        ),
        (
            "class-name",
            partial(
                _generic_name_check,
                config["class-name"],
                rule_name_tokens["classname_stmt"],
                "class-name",
                'Class name "{}" is not valid',
            ),
        ),
        (
            "signal-name",
            partial(
                _generic_name_check,
                config["signal-name"],
                rule_name_tokens["signal_stmt"],
                "signal-name",
                'Signal name "{}" is not valid',
            ),
        ),
        (
            "enum-name",
            partial(
                _generic_name_check,
                config["enum-name"],
                rule_name_tokens["enum_named"],
                "enum-name",
                'Enum name "{}" is not valid',
            ),
        ),
        (
            "enum-element-name",
            partial(
                _generic_name_check,
                config["enum-element-name"],
                rule_name_tokens["enum_element"],
                "enum-element-name",
                'Enum element name "{}" is not valid',
            ),
        ),
        (
            "loop-variable-name",
            partial(
                _generic_name_check,
                config["loop-variable-name"],
                rule_name_tokens["for_stmt"],
                "loop-variable-name",
                'Loop variable name "{}" is not valid',
            ),
        ),
        (
            "function-argument-name",
            partial(
                _generic_name_check,
                config["function-argument-name"],
                rule_name_tokens["func_arg_regular"]
                + rule_name_tokens["func_arg_inf"]
                + rule_name_tokens["func_arg_typed"],
                "function-argument-name",
                'Function argument name "{}" is not valid',
            ),
        ),
        (
            "function-variable-name",
            partial(
                _generic_name_check,
                config["function-variable-name"],
                _gather_rule_name_tokens(
                    parse_tree,
                    ["func_var_stmt"],
                    lambda x: not _has_load_or_preload_call_expr(x),
                )["func_var_stmt"],
                "function-variable-name",
                'Function-scope variable name "{}" is not valid',
            ),
        ),
        (
            "function-preload-variable-name",
            partial(
                _generic_name_check,
                config["function-preload-variable-name"],
                _gather_rule_name_tokens(
                    parse_tree,
                    ["func_var_stmt"],
                    _has_preload_call_expr,
                )["func_var_stmt"],
                "function-preload-variable-name",
                'Function-scope preload variable name "{}" is not valid',
            ),
        ),
        (
            "constant-name",
            partial(
                _generic_name_check,
                config["constant-name"],
                _gather_rule_name_tokens(
                    parse_tree,
                    ["const_stmt"],
                    lambda x: not _has_load_or_preload_call_expr(x),
                )["const_stmt"],
                "constant-name",
                'Constant name "{}" is not valid',
            ),
        ),
        (
            "load-constant-name",
            partial(
                _generic_name_check,
                config["load-constant-name"],
                _gather_rule_name_tokens(
                    parse_tree,
                    ["const_stmt"],
                    _has_load_or_preload_call_expr,
                )["const_stmt"],
                "load-constant-name",
                'Constant (load/preload) name "{}" is not valid',
            ),
        ),
        (
            "class-variable-name",
            partial(
                _generic_name_check,
                config["class-variable-name"],
                _gather_rule_name_tokens(
                    parse_tree,
                    ["class_var_stmt"],
                    lambda x: not _has_load_or_preload_call_expr(x),
                )["class_var_stmt"],
                "class-variable-name",
                'Class-scope variable name "{}" is not valid',
            ),
        ),
        (
            "class-load-variable-name",
            partial(
                _generic_name_check,
                config["class-load-variable-name"],
                _gather_rule_name_tokens(
                    parse_tree,
                    ["class_var_stmt"],
                    _has_load_or_preload_call_expr,
                )["class_var_stmt"],
                "class-load-variable-name",
                'Class-scope load/preload variable name "{}" is not valid',
            ),
        ),
    ]
    problem_clusters = map(
        lambda x: x[1]() if x[0] not in disable else [], checks_to_run_wo_tree
    )
    problems = [problem for cluster in problem_clusters for problem in cluster]
    return problems


def _generic_name_check(
    name_regex, name_tokens, problem_name, description_template
) -> List[Problem]:
    problems = []
    name_regex = re.compile(name_regex)
    for name_token in name_tokens:
        name = name_token.value
        if name_regex.fullmatch(name) is None:
            problems.append(
                Problem(
                    name=problem_name,
                    description=description_template.format(name),
                    line=name_token.line,
                    column=name_token.column,
                )
            )
    return problems


def _gather_rule_name_tokens(
    parse_tree: Tree, rules, predicate=lambda _: True
) -> Dict[str, List[str]]:
    name_tokens_per_rule = {rule: [] for rule in rules}  # type: Dict[str, List[str]]
    for node in parse_tree.iter_subtrees():
        if isinstance(node, Tree) and node.data in rules:
            rule_name = node.data
            name_token = find_name_token_among_children(node)
            if name_token is None:
                name_token = find_name_token_among_children(node.children[0])
                predicate_outcome = predicate(node.children[0])
            else:
                predicate_outcome = predicate(node)
            assert name_token is not None
            if predicate_outcome:
                name_tokens_per_rule[rule_name].append(name_token)
    return name_tokens_per_rule


def _has_load_or_preload_call_expr(tree: Tree) -> bool:
    return _has_call_expr_name_in(tree, ["load", "preload"])


def _has_preload_call_expr(tree: Tree) -> bool:
    return _has_call_expr_name_in(tree, ["preload"])


def _has_call_expr_name_in(tree: Tree, legal_names: List[str]) -> bool:
    for child in tree.children:
        if isinstance(child, Tree) and child.data == "expr":
            expr = child
            if (
                len(expr.children) == 1
                and isinstance(expr.children[0], Tree)
                and expr.children[0].data == "standalone_call"
            ):
                standalone_call = expr.children[0]
                name_token = find_name_token_among_children(standalone_call)
                assert name_token is not None
                name = name_token.value
                return name in legal_names
    return False
