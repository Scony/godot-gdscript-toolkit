from functools import partial
from types import MappingProxyType
from typing import Callable, List, Tuple

from lark import Token, Tree

from ..common.utils import find_name_token_among_children

from .problem import Problem
from .helpers import is_function_public


def lint(parse_tree: Tree, config: MappingProxyType) -> List[Problem]:
    disable = config["disable"]
    checks_to_run_w_tree = [
        (
            "private-method-call",
            _private_method_call_check,
        ),
        (
            "class-definitions-order",
            partial(_class_definitions_order_check, config["class-definitions-order"]),
        ),
    ]  # type: List[Tuple[str, Callable]]
    problem_clusters = (
        x[1](parse_tree) if x[0] not in disable else [] for x in checks_to_run_w_tree
    )
    problems = [problem for cluster in problem_clusters for problem in cluster]
    return problems


def _private_method_call_check(parse_tree: Tree) -> List[Problem]:
    problems = []
    for getattr_call in parse_tree.find_data("getattr_call"):
        _getattr = getattr_call.children[0]
        callee_name_token = _getattr.children[-1]
        callee_name = callee_name_token.value
        called = _getattr.children[-3]
        if (
            isinstance(called, Token)
            and called.type == "NAME"
            and called.value == "self"
        ):
            continue
        if not _is_method_private(callee_name):
            continue
        problems.append(
            Problem(
                name="private-method-call",
                description='Private method "{}" has been called'.format(callee_name),
                line=callee_name_token.line,
                column=callee_name_token.column,
            )
        )
    return problems


def _is_method_private(method_name: str) -> bool:
    return method_name.startswith("_")  # TODO: consider making configurable


def _class_definitions_order_check(_order, _parse_tree: Tree) -> List[Problem]:
    return []


def _class_definitions_order_check_for_class(
    _class_name: str, _class_children, _order
) -> List[Problem]:
    return []


def _class_var_stmt_visibility(class_var_stmt) -> str:
    some_var_stmt = class_var_stmt.children[0]
    name_token = find_name_token_among_children(some_var_stmt)
    return "pub" if is_function_public(name_token.value) else "prv"  # type: ignore
