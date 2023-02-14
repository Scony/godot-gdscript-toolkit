from functools import partial
from types import MappingProxyType
from typing import Callable, List, Tuple

from lark import Token, Tree

from ..common.ast import AbstractSyntaxTree, Class, Statement, Annotation
from ..common.utils import find_name_token_among_children, get_line, get_column

from .problem import Problem
from .helpers import is_function_public


def lint(parse_tree: Tree, config: MappingProxyType) -> List[Problem]:
    disable = config["disable"]
    checks_to_run_w_tree = [
        (
            "private-method-call",
            _private_method_call_check,
        ),
    ]  # type: List[Tuple[str, Callable]]
    problem_clusters = (
        function(parse_tree) if name not in disable else []
        for name, function in checks_to_run_w_tree
    )
    problems = [problem for cluster in problem_clusters for problem in cluster]
    checks_to_run_w_ast = [
        (
            "class-definitions-order",
            partial(_class_definitions_order_check, config["class-definitions-order"]),
        ),
    ]
    ast = AbstractSyntaxTree(parse_tree)
    problem_clusters = (
        function(ast) if name not in disable else []
        for name, function in checks_to_run_w_ast
    )
    problems += [problem for cluster in problem_clusters for problem in cluster]
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
        if is_function_public(callee_name):
            continue
        problems.append(
            Problem(
                name="private-method-call",
                description='Private method "{}" has been called'.format(callee_name),
                line=get_line(callee_name_token),
                column=get_column(callee_name_token),
            )
        )
    return problems


def _class_definitions_order_check(
    order: List[str], ast: AbstractSyntaxTree
) -> List[Problem]:
    return [
        problem
        for a_class in ast.all_classes
        for problem in _class_definitions_order_check_for_class(a_class, order)
    ]


def _class_definitions_order_check_for_class(
    a_class: Class, order: List[str]
) -> List[Problem]:
    problems = []
    current_section = order[0]
    for statement in a_class.statements:
        if _is_statement_irrelevant(statement):
            continue
        current_section_rank = order.index(current_section)
        statement_section = _map_statement_to_section(statement)
        section_rank = order.index(statement_section)
        if section_rank >= current_section_rank:
            current_section = statement_section
        else:
            problems.append(
                Problem(
                    name="class-definitions-order",
                    description="Definition out of order in {}".format(a_class.name),
                    line=get_line(statement.lark_node),
                    column=get_column(statement.lark_node),
                )
            )
    return problems


def _is_statement_irrelevant(statement: Statement) -> bool:
    if statement.kind == "pass_stmt":
        return True
    if statement.kind == "annotation":
        return Annotation(statement.lark_node).name != "tool"
    if statement.kind == "class_def":
        return True
    return False


# pylint: disable-next=too-many-return-statements
def _map_statement_to_section(statement: Statement) -> str:
    if statement.kind == "class_var_stmt":
        if any(
            annotation.name.startswith("export") for annotation in statement.annotations
        ):
            return "exports"
        if any(annotation.name == "onready" for annotation in statement.annotations):
            return "onready{}vars".format(
                _class_var_stmt_visibility(statement.lark_node)
            )
        return "{}vars".format(_class_var_stmt_visibility(statement.lark_node))
    if statement.kind == "signal_stmt":
        return "signals"
    if statement.kind == "extends_stmt":
        return "extends"
    if statement.kind == "enum_stmt":
        return "enums"
    if statement.kind == "classname_stmt":
        return "classnames"
    if statement.kind == "const_stmt":
        return "consts"
    if (
        statement.kind == "annotation"
        and Annotation(statement.lark_node).name == "tool"
    ):
        return "tools"
    if statement.kind == "func_def":
        return "others"
    if statement.kind == "static_func_def":
        return "others"
    raise NotImplementedError


def _class_var_stmt_visibility(class_var_stmt: Tree) -> str:
    some_var_stmt = class_var_stmt.children[0]
    name_token = find_name_token_among_children(some_var_stmt)
    return "pub" if is_function_public(name_token.value) else "prv"  # type: ignore
