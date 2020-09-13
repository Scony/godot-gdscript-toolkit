from functools import partial
from types import MappingProxyType
from typing import Callable, List, Tuple

from lark import Token, Tree

from .problem import Problem
from .helpers import find_name_token_among_children, is_function_public


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
    problem_clusters = map(
        lambda x: x[1](parse_tree) if x[0] not in disable else [], checks_to_run_w_tree
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


def _class_definitions_order_check(order, parse_tree: Tree) -> List[Problem]:
    problems = _class_definitions_order_check_for_class(
        "global scope", parse_tree.children, order
    )
    for class_def in parse_tree.find_data("class_def"):
        class_name = class_def.children[0].value
        problems += _class_definitions_order_check_for_class(
            "class {}".format(class_name), class_def.children, order
        )
    return problems


def _class_definitions_order_check_for_class(
    class_name: str, class_children, order
) -> List[Problem]:
    stmt_to_section_mapping = {
        "tool_stmt": "tools",
        "signal_stmt": "signals",
        "extends_stmt": "extends",
        "classname_stmt": "classnames",
        "const_stmt": "consts",
        "export_stmt": "exports",
        "enum_def": "enums",
    }
    visibility_dependent_stmt_to_section_mapping = {
        "class_var_stmt": {"pub": "pubvars", "prv": "prvvars"},
        "onready_stmt": {"pub": "onreadypubvars", "prv": "onreadyprvvars"},
    }
    problems = []
    current_section = order[0]
    for class_child in class_children:
        if not isinstance(class_child, Tree):
            continue
        stmt = class_child.data
        if stmt == "class_var_stmt":
            visibility = _class_var_stmt_visibility(class_child)
            section = visibility_dependent_stmt_to_section_mapping[stmt][visibility]
        elif stmt == "onready_stmt":
            class_var_stmt = class_child.children[0]
            visibility = _class_var_stmt_visibility(class_var_stmt)
            section = visibility_dependent_stmt_to_section_mapping[stmt][visibility]
        else:
            section = stmt_to_section_mapping.get(stmt, "others")
        section_rank = order.index(section)
        if section_rank >= order.index(current_section):
            current_section = section
        else:
            problems.append(
                Problem(
                    name="class-definitions-order",
                    description="Definition out of order in {}".format(class_name),
                    line=class_child.line,
                    column=class_child.column,
                )
            )
    return problems


def _class_var_stmt_visibility(class_var_stmt) -> str:
    some_var_stmt = class_var_stmt.children[0]
    name_token = find_name_token_among_children(some_var_stmt)
    return "pub" if is_function_public(name_token.value) else "prv"
