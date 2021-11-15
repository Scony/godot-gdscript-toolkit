from functools import partial
from typing import List, Callable, Dict

from ..parser import parser
from ..formatter.context import Context
from ..formatter.types import Node  # TODO: extract to common


def convert_code(gdscript_code: str) -> str:
    parse_tree = parser.parse(
        gdscript_code, gather_metadata=True
    )  # TODO: is metadata needed?
    context = Context(
        indent=0,
        previously_processed_line_number=-1,
        max_line_length=-1,
        gdscript_code_lines=[],
        standalone_comments=[],
        inline_comments=[],
    )  # TODO: create custom (small) context
    converted_lines = _convert_block(parse_tree.children, context)
    return "\n".join(converted_lines + [""])


def _convert_block(statements: List[Node], context: Context) -> List[str]:
    converted_lines = []  # List[str]
    for statement in statements:
        converted_lines += _convert_statement(statement, context)
    return converted_lines


def _convert_statement(statement: Node, context: Context) -> List[str]:
    handlers = {
        # class statements:
        "tool_stmt": _ignore,
        "pass_stmt": lambda s, c: [f"{c.indent_string}pass"],
        "class_var_stmt": _convert_first_child_as_statement,
        "var_empty": lambda s, c: [f"{c.indent_string}{s.children[0].value} = None"],
        "var_assigned": _convert_var_statement_with_expression,
        "var_typed": lambda s, c: [f"{c.indent_string}{s.children[0].value} = None"],
        "var_typed_assgnd": _convert_var_statement_with_expression,
        "var_inf": _convert_var_statement_with_expression,
        "extends_stmt": _ignore,
        "class_def": _convert_class_def,
        "func_def": _convert_func_def,
        "enum_def": _ignore,  # TODO: implement
        "classname_stmt": _ignore,
        "classname_extends_stmt": _ignore,
        "signal_stmt": _ignore,
        "docstr_stmt": lambda s, c: [
            f"{c.indent_string}{s.children[0].children[0].value}"
        ],
        "const_stmt": lambda s, c: [
            "{}{} = {}".format(
                c.indent_string,
                s.children[1].value,
                _convert_expression_to_str(s.children[-1]),
            )
        ],
        "export_stmt": _convert_export_statement,
        "onready_stmt": lambda s, c: _convert_statement(s.children[-1], c),
        "puppet_var_stmt": _convert_first_child_as_statement,
        "static_func_def": _convert_first_child_as_statement,
        "remote_func_def": _convert_first_child_as_statement,
        "remotesync_func_def": _convert_first_child_as_statement,
        "master_func_def": _convert_first_child_as_statement,
        "mastersync_func_def": _convert_first_child_as_statement,
        "puppet_func_def": _convert_first_child_as_statement,
        "puppetsync_func_def": _convert_first_child_as_statement,
        "sync_func_def": _convert_first_child_as_statement,
        # func statements:
        "func_var_stmt": _convert_first_child_as_statement,
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
        "match_stmt": _convert_match_statement,
        "match_branch": partial(_convert_branch_with_expression, "elif"),
    }  # type: Dict[str, Callable]
    return handlers[statement.data](statement, context)


def _ignore(_statement: Node, context: Context) -> List[str]:
    return [f"{context.indent_string}pass"]


def _convert_first_child_as_statement(statement: Node, context: Context) -> List[str]:
    return _convert_statement(statement.children[0], context)


def _convert_var_statement_with_expression(
    statement: Node, context: Context
) -> List[str]:
    return [
        "{}{} = {}".format(
            context.indent_string,
            statement.children[0].value,
            _convert_expression_to_str(statement.children[-1]),
        )
    ]


def _convert_export_statement(statement: Node, context: Context) -> List[str]:
    actual_statement = statement.children[0]
    if actual_statement.children[-1].data == "setget":
        return _convert_statement(actual_statement.children[-2], context)
    return _convert_statement(actual_statement.children[-1], context)


def _convert_class_def(statement: Node, context: Context) -> List[str]:
    return [
        f"{context.indent_string}class {statement.children[0].value}:"
    ] + _convert_block(statement.children[1:], context.create_child_context(-1))


def _convert_func_def(statement: Node, context: Context) -> List[str]:
    # TODO: handle func args
    return [
        f"{context.indent_string}def {statement.children[0].children[0].value}():",
    ] + _convert_block(statement.children[1:], context.create_child_context(-1))


def _convert_branch_with_expression(
    prefix: str, statement: Node, context: Context
) -> List[str]:
    return [
        "{}{} {}:".format(
            context.indent_string,
            prefix,
            _convert_expression_to_str(statement.children[0]),
        ),
    ] + _convert_block(statement.children[1:], context.create_child_context(-1))


def _convert_match_statement(statement: Node, context: Context) -> List[str]:
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
