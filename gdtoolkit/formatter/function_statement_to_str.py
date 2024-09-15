from importlib import import_module

from lark import Tree


def function_statement_to_str(statement: Tree) -> str:
    expression_to_str_module = import_module("gdtoolkit.formatter.expression_to_str")
    expression_to_str = expression_to_str_module.expression_to_str
    standalone_expression_to_str = expression_to_str_module.standalone_expression_to_str
    return {
        "pass_stmt": lambda _: "pass",
        "func_var_stmt": lambda s: function_statement_to_str(s.children[0]),
        "const_stmt": lambda s: function_statement_to_str(s.children[0]),
        "expr_stmt": lambda s: expression_to_str(s.children[0]),  # TODO: standalone?
        "return_stmt": lambda s: f"return {standalone_expression_to_str(s.children[0])}",
        "break_stmt": _not_implemented,
        "breakpoint_stmt": lambda _: "breakpoint",
        "continue_stmt": _not_implemented,
        "if_stmt": _not_implemented,
        "while_stmt": _not_implemented,
        "for_stmt": _not_implemented,
        "for_stmt_typed": _not_implemented,
        "match_stmt": _not_implemented,
        "annotation": _not_implemented,
        # statement fragments:
        "func_var_empty": lambda s: f"var {s.children[0].value}",
        "func_var_assigned": lambda s: "var {} = {}".format(
            s.children[0].value, standalone_expression_to_str(s.children[1])
        ),
        "func_var_inf": lambda s: "var {} := {}".format(
            s.children[0].value, standalone_expression_to_str(s.children[1])
        ),
        "func_var_typed": lambda s: "var {}: {}".format(
            s.children[0].value, standalone_expression_to_str(s.children[1])
        ),
        "func_var_typed_assgnd": lambda s: "var {}: {} = {}".format(
            s.children[0].value,
            s.children[1].value,
            standalone_expression_to_str(s.children[2]),
        ),
        "const_assigned": lambda s: "const {} = {}".format(
            s.children[0].value, standalone_expression_to_str(s.children[1])
        ),
        "const_typed_assigned": lambda s: "const {}: {} = {}".format(
            s.children[0].value,
            s.children[1].value,
            standalone_expression_to_str(s.children[2]),
        ),
        "const_inf": lambda s: "const {} := {}".format(
            s.children[0].value, standalone_expression_to_str(s.children[1])
        ),
        "match_branch": _not_implemented,
        "guarded_match_branch": _not_implemented,
    }[statement.data](statement)


def _not_implemented(statement: Tree) -> str:
    raise NotImplementedError
