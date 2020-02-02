from types import MappingProxyType
from typing import List

from .problem import Problem
from ..parser import parser
from . import basic_checks, class_checks, design_checks, format_checks, name_checks

PASCAL_CASE = r"([A-Z][a-z0-9]*)+"
SNAKE_CASE = r"[a-z][a-z0-9]*(_[a-z0-9]+)*"
PRIVATE_SNAKE_CASE = r"_?{}".format(SNAKE_CASE)
UPPER_SNAKE_CASE = r"[A-Z][A-Z0-9]*(_[A-Z0-9]+)*"

DEFAULT_CONFIG = MappingProxyType(
    {
        # check control
        "disable": [],
        # name checks
        "function-name": r"(_on_{}(_[a-z0-9]+)*|{})".format(
            PASCAL_CASE, PRIVATE_SNAKE_CASE
        ),
        "class-name": PASCAL_CASE,
        "sub-class-name": r"_?{}".format(PASCAL_CASE),
        "signal-name": SNAKE_CASE,
        "class-variable-name": PRIVATE_SNAKE_CASE,
        "class-load-variable-name": r"({}|{})".format(PASCAL_CASE, PRIVATE_SNAKE_CASE),
        "function-variable-name": SNAKE_CASE,
        "function-load-variable-name": PASCAL_CASE,
        "function-argument-name": PRIVATE_SNAKE_CASE,
        "loop-variable-name": PRIVATE_SNAKE_CASE,
        "enum-name": PASCAL_CASE,
        "enum-element-name": UPPER_SNAKE_CASE,
        "constant-name": UPPER_SNAKE_CASE,
        "load-constant-name": r"({}|{})".format(PASCAL_CASE, UPPER_SNAKE_CASE),
        # basic checks
        "duplicated-load": None,
        "expression-not-assigned": None,
        "unnecessary-pass": None,
        "unused-argument": None,
        "comparison-with-itself": None,
        # not-in-loop (break/continue) # check in godot
        # duplicate-argument-name # check in godot
        # self-assigning-variable # check in godot
        # comparison-with-callable
        # duplicate-key # check in godot
        # unreachable # check in godot
        # using-constant-test # check in godot
        # class checks
        "private-method-call": None,
        "class-definitions-order": [
            "tools",
            "classnames",
            "extends",
            "signals",
            "enums",
            "consts",
            "exports",
            "pubvars",
            "prvvars",
            "onreadypubvars",
            "onreadyprvvars",
            "others",
        ],
        # useless-super-delegation
        # design checks
        # max-locals
        # max-returns
        # max-branches
        # max-statements
        # max-attributes
        "max-public-methods": 20,
        # max-nested-blocks
        "function-arguments-number": 10,
        # format checks
        "max-file-lines": 1000,
        "trailing-whitespace": None,
        "max-line-length": 100,
        "mixed-tabs-and-spaces": None,
        # misc
        # no-else-return
        # never-returning-function # for non-void, typed functions
        # simplify-boolean-expression
        # consider-using-in
        # inconsistent-return-statements
        # redefined-argument-from-local
        # chained-comparison
        # unused-variable
        # pointless-statement
        # magic values
        # misc-redundant-expression
        # https://clang.llvm.org/extra/clang-tidy/checks/misc-redundant-expression.html
        # readability-magic-numbers
        # https://clang.llvm.org/extra/clang-tidy/checks/readability-magic-numbers.html
        # bugprone-virtual-near-miss
        # ~ https://clang.llvm.org/extra/clang-tidy/checks/list.html
    }
)


def lint_code(
    gdscript_code: str, config: MappingProxyType = DEFAULT_CONFIG
) -> List[Problem]:
    parse_tree = parser.parse(gdscript_code, gather_metadata=True)
    problems = design_checks.lint(parse_tree, config)
    problems += format_checks.lint(gdscript_code, config)
    problems += name_checks.lint(parse_tree, config)
    problems += class_checks.lint(parse_tree, config)
    problems += basic_checks.lint(parse_tree, config)
    return problems
