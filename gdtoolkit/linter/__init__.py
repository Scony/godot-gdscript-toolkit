import re
from collections import defaultdict
from types import MappingProxyType
from typing import List, Dict, Set

from .problem import Problem
from ..parser import parser
from .types import Range
from . import (
    basic_checks,
    class_checks,
    design_checks,
    format_checks,
    name_checks,
    misc_checks,
)

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
        "function-preload-variable-name": PASCAL_CASE,
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
        "tab-characters": 1,
        "mixed-tabs-and-spaces": None,
        # misc
        "excluded_directories": {".git"},
        "no-elif-return": None,
        "no-else-return": None,
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
    problems += misc_checks.lint(parse_tree, config)

    problems_to_lines_where_they_are_inactive = _fetch_problem_inactivity_lines(
        gdscript_code
    )
    problems = [
        problem
        for problem in problems
        if problem.name not in problems_to_lines_where_they_are_inactive
        or problem.line not in problems_to_lines_where_they_are_inactive[problem.name]
    ]

    return problems


def _fetch_problem_inactivity_lines(gdscript_code: str) -> Dict[str, Set[int]]:
    problem_inactivity_lines = defaultdict(set)
    lines_to_ignored_problems = _fetch_ignored_problems_per_lines(gdscript_code)
    for line, problems in lines_to_ignored_problems.items():
        for problem in problems:
            problem_inactivity_lines[problem].add(line)
            problem_inactivity_lines[problem].add(line + 1)
    problem_inactivity_ranges = _fetch_problem_inactivity_ranges(gdscript_code)
    # TODO: use interval trees if to speed up
    for problem, inactivity_ranges in problem_inactivity_ranges.items():
        for a_range in inactivity_ranges:
            problem_inactivity_lines[problem].update(
                range(a_range.begin, a_range.end + 1)
            )
    return problem_inactivity_lines


def _fetch_ignored_problems_per_lines(gdscript_code: str) -> Dict[int, Set[str]]:
    lines = gdscript_code.splitlines()
    compiled_regex = re.compile(r"#\s*gdlint\s*:\s*ignore\s*=\s*([^,]+(,[^,]+)*)")
    lines_to_ignored_problems: Dict[int, Set[str]] = defaultdict(set)
    for line_no, line in enumerate(lines, start=1):
        pattern_matching_outcome = compiled_regex.search(line)
        if pattern_matching_outcome is not None:
            ignored_problems = [
                p.strip() for p in pattern_matching_outcome.group(1).split(",")
            ]
            lines_to_ignored_problems[line_no].update(ignored_problems)
    return lines_to_ignored_problems


def _fetch_problem_inactivity_ranges(gdscript_code: str) -> Dict[str, List[Range]]:
    problem_inactivity_ranges = defaultdict(list)
    lines = gdscript_code.splitlines()
    last_line_no = len(lines)

    problem_range_begins = _fetch_problem_disabling_lines(lines)
    for problem, range_begins in problem_range_begins.items():
        for range_begin in range_begins:
            problem_inactivity_ranges[problem].append(Range(range_begin, last_line_no))

    problem_range_ends = _fetch_problem_enabling_lines(lines)
    for problem, range_ends in problem_range_ends.items():
        for range_end in range_ends:
            for a_range in problem_inactivity_ranges[problem]:
                if range_end < a_range.end:
                    a_range.end = range_end

    return problem_inactivity_ranges


def _fetch_problem_disabling_lines(lines: List[str]) -> Dict[str, List[int]]:
    compiled_regex = re.compile(r"#\s*gdlint\s*:\s*disable\s*=\s*([^,]+(,[^,]+)*)")
    problem_to_disabling_lines = defaultdict(list)
    for line_no, line in enumerate(lines, start=1):
        pattern_matching_outcome = compiled_regex.search(line)
        if pattern_matching_outcome is not None:
            ignored_problems = [
                p.strip() for p in pattern_matching_outcome.group(1).split(",")
            ]
            for problem in ignored_problems:
                problem_to_disabling_lines[problem].append(line_no + 1)
    return problem_to_disabling_lines


def _fetch_problem_enabling_lines(lines: List[str]) -> Dict[str, List[int]]:
    compiled_regex = re.compile(r"#\s*gdlint\s*:\s*enable\s*=\s*([^,]+(,[^,]+)*)")
    problem_to_enabling_lines = defaultdict(list)
    for line_no, line in enumerate(lines, start=1):
        pattern_matching_outcome = compiled_regex.search(line)
        if pattern_matching_outcome is not None:
            ignored_problems = [
                p.strip() for p in pattern_matching_outcome.group(1).split(",")
            ]
            for problem in ignored_problems:
                problem_to_enabling_lines[problem].append(line_no)
    return problem_to_enabling_lines
