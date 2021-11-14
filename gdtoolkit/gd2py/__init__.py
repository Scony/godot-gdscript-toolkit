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
        "class_var_stmt": lambda s, c: _convert_statement(s.children[0], c),
        "var_empty": lambda s, c: [f"{c.indent_string}{s.children[0].value} = None"],
        "var_assigned": lambda s, c: [],  # TODO: implement
        "var_typed": lambda s, c: [f"{c.indent_string}{s.children[0].value} = None"],
        "var_typed_assgnd": lambda s, c: [],  # TODO: implement
        "var_inf": lambda s, c: [],  # TODO: implement
        "extends_stmt": _ignore,
        "class_def": _convert_class_def,
        "func_def": lambda s, c: [],  # TODO: implement
        "enum_def": lambda s, c: [],  # TODO: implement
        "classname_stmt": _ignore,
        # "classname_extends_stmt": _format_classname_extends_statement,
        "signal_stmt": _ignore,
        "docstr_stmt": lambda s, c: [],  # TODO: implement
        "const_stmt": lambda s, c: [],  # TODO: implement
        "export_stmt": lambda s, c: [],  # TODO: implement
        "onready_stmt": lambda s, c: [],  # TODO: implement
        # "puppet_var_stmt": lambda s, c: format_var_statement(
        # "static_func_def": partial(
        # "remote_func_def": partial(
        # "remotesync_func_def": partial(
        # "master_func_def": partial(
        # "mastersync_func_def": partial(
        # "puppet_func_def": partial(
        # "puppetsync_func_def": partial(
        # "sync_func_def":
        # ----
    }  # type: Dict[str, Callable]
    return handlers[statement.data](statement, context)


def _ignore(_statement: Node, _context: Context) -> List[str]:
    return []


def _convert_class_def(statement: Node, context: Context) -> List[str]:
    return [
        f"{context.indent_string}class {statement.children[0].value}:"
    ] + _convert_block(statement.children[1:], context.create_child_context(-1))
