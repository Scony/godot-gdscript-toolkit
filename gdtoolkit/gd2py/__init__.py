from functools import partial
from typing import List, Callable, Dict

from lark import Tree

from ..common.types import Node
from ..parser import parser
from ..formatter.context import Context


def convert_code(gdscript_code: str) -> str:
    parse_tree = parser.parse(
        gdscript_code, gather_metadata=True
    )  # TODO: is metadata needed?
    context = Context(
        single_indent_size=1,
        single_indent_string="\t",
        previously_processed_line_number=-1,
        max_line_length=-1,
        gdscript_code_lines=[],
        standalone_comments=[],
        inline_comments=[],
    )  # TODO: create custom (small) context
    converted_lines = _convert_block(parse_tree.children, context)
    return "\n".join(converted_lines + [""])


def _convert_block(statements: List[Tree], context: Context) -> List[str]:
    converted_lines = []  # List[str]
    for statement in statements:
        converted_lines += _convert_statement(statement, context)
    return converted_lines


def _convert_statement(statement: Tree, context: Context) -> List[str]:
    handlers = {
        # class statements:
        "annotation": _ignore,
        "pass_stmt": lambda s, c: [f"{c.indent_string}pass"],
        "class_var_stmt": _convert_first_child_as_statement,
        "static_class_var_stmt": _convert_first_child_as_statement,
        "class_var_empty": lambda s, c: [
            f"{c.indent_string}{s.children[0].value} = None"
        ],
        "class_var_assigned": _convert_var_statement_with_expression,
        "class_var_typed": lambda s, c: [
            f"{c.indent_string}{s.children[0].value} = None"
        ],
        "class_var_typed_assgnd": _convert_var_statement_with_expression,
        "class_var_inf": _convert_var_statement_with_expression,
        "extends_stmt": _pass,
        "class_def": _convert_class_def,
        "func_def": _convert_func_def,
        "enum_stmt": _pass,  # TODO: implement
        "classname_stmt": _pass,
        "property_body_def": _pass,
        "classname_extends_stmt": _pass,
        "signal_stmt": _pass,
        "const_stmt": lambda s, c: [
            "{}{} = {}".format(
                c.indent_string,
                s.children[0].children[0].value,
                _convert_expression_to_str(s.children[-1]),
            )
        ],
        "static_func_def": _convert_first_child_as_statement,
        "docstr_stmt": _pass,
        # func statements:
        "func_var_stmt": _convert_first_child_as_statement,
        "func_var_empty": lambda s, c: [
            f"{c.indent_string}{s.children[0].value} = None"
        ],
        "func_var_assigned": _convert_var_statement_with_expression,
        "func_var_typed": lambda s, c: [
            f"{c.indent_string}{s.children[0].value} = None"
        ],
        "func_var_typed_assgnd": _convert_var_statement_with_expression,
        "func_var_inf": _convert_var_statement_with_expression,
        "expr_stmt": _convert_first_child_as_statement,
        "expr": lambda s, c: [
            f"{c.indent_string}{_convert_expression_to_str(s.children[0])}"
        ],
        "return_stmt": lambda s, c: [
            f"{c.indent_string}return"
            + (
                f" {_convert_expression_to_str(s.children[0])}"
                if len(s.children) > 0
                else ""
            )
        ],
        "break_stmt": lambda s, c: [f"{c.indent_string}break"],
        "breakpoint_stmt": lambda s, c: [f"{c.indent_string}breakpoint"],
        "continue_stmt": lambda s, c: [f"{c.indent_string}continue"],
        "if_stmt": lambda s, c: _convert_block(s.children, c),
        "if_branch": partial(_convert_branch_with_expression, "if"),
        "elif_branch": partial(_convert_branch_with_expression, "elif"),
        "else_branch": lambda s, c: [f"{c.indent_string}else:"]
        + _convert_block(s.children, c.create_child_context(-1)),
        "while_stmt": partial(_convert_branch_with_expression, "while"),
        "for_stmt": lambda s, c: [
            "{}for {} in {}:".format(
                c.indent_string,
                s.children[0].value,
                _convert_expression_to_str(s.children[1]),
            )
        ]
        + _convert_block(s.children[2:], c.create_child_context(-1)),
        "for_stmt_typed": lambda s, c: [
            "{}for {} in {}:".format(
                c.indent_string,
                s.children[0].value,
                _convert_expression_to_str(s.children[2]),
            )
        ]
        + _convert_block(s.children[3:], c.create_child_context(-2)),
        "match_stmt": _convert_match_statement,
        "match_branch": partial(_convert_branch_with_expression, "elif"),
        "guarded_match_branch": partial(_convert_branch_with_expression, "elif"),
    }  # type: Dict[str, Callable]
    return handlers[statement.data](statement, context)


def _ignore(_statement: Node, _context: Context) -> List[str]:
    return []


def _pass(_statement: Node, context: Context) -> List[str]:
    return [f"{context.indent_string}pass"]


def _convert_first_child_as_statement(statement: Tree, context: Context) -> List[str]:
    return _convert_statement(statement.children[0], context)


def _convert_var_statement_with_expression(
    statement: Tree, context: Context
) -> List[str]:
    return [
        "{}{} = {}".format(
            context.indent_string,
            statement.children[0].value,
            _convert_expression_to_str(statement.children[-1]),
        )
    ]


def _convert_export_statement(statement: Tree, context: Context) -> List[str]:
    actual_statement = statement.children[0]
    if actual_statement.children[-1].data == "setget":
        return _convert_statement(actual_statement.children[-2], context)
    return _convert_statement(actual_statement.children[-1], context)


def _convert_class_def(statement: Tree, context: Context) -> List[str]:
    return [
        f"{context.indent_string}class {statement.children[0].value}:"
    ] + _convert_block(statement.children[1:], context.create_child_context(-1))


def _convert_func_def(statement: Tree, context: Context) -> List[str]:
    # TODO: handle func args
    return [
        f"{context.indent_string}def {statement.children[0].children[0].value}():",
    ] + _convert_block(statement.children[1:], context.create_child_context(-1))


def _convert_branch_with_expression(
    prefix: str, statement: Tree, context: Context
) -> List[str]:
    return [
        "{}{} {}:".format(
            context.indent_string,
            prefix,
            _convert_expression_to_str(statement.children[0]),
        ),
    ] + _convert_block(statement.children[1:], context.create_child_context(-1))


def _convert_match_statement(statement: Tree, context: Context) -> List[str]:
    # TODO: proper implementation
    return [
        "{}if {}:".format(
            context.indent_string, _convert_expression_to_str(statement.children[0])
        ),
        f"{context.create_child_context(-1).indent_string}pass",
    ] + _convert_block(statement.children[1:], context)


def _convert_expression_to_str(_expression: Node) -> str:
    # TODO: handle
    return "1"
