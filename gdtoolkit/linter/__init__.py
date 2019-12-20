from functools import partial
from types import MappingProxyType

from lark import Tree

from ..parser import parser_with_metadata_gathering
from .. import Problem
from . import name_checks, class_checks, basic_checks

PASCAL_CASE = r'([A-Z][a-z0-9]*)+'
SNAKE_CASE = r'[a-z][a-z0-9]*(_[a-z0-9]+)*'
PRIVATE_SNAKE_CASE = r'_?{}'.format(SNAKE_CASE)
UPPER_SNAKE_CASE = r'[A-Z][A-Z0-9]*(_[A-Z0-9]+)*'

DEFAULT_CONFIG = MappingProxyType({
    # check control
    'disable': [],
    # name checks
    'function-name': r'(_on_{}(_[a-z0-9]+)*|{})'.format(PASCAL_CASE, PRIVATE_SNAKE_CASE),
    'class-name': PASCAL_CASE,
    'sub-class-name': r'_?{}'.format(PASCAL_CASE),
    'signal-name': SNAKE_CASE,
    'class-variable-name': PRIVATE_SNAKE_CASE,
    'class-load-variable-name': r'({}|{})'.format(PASCAL_CASE, PRIVATE_SNAKE_CASE),
    'function-variable-name': SNAKE_CASE,
    'function-load-variable-name': PASCAL_CASE,
    'function-argument-name': PRIVATE_SNAKE_CASE,
    'loop-variable-name': PRIVATE_SNAKE_CASE,
    'enum-name': PASCAL_CASE,
    'enum-element-name': UPPER_SNAKE_CASE,
    'constant-name': UPPER_SNAKE_CASE,
    'load-constant-name': r'({}|{})'.format(PASCAL_CASE, UPPER_SNAKE_CASE),
    # basic checks
    # not-in-loop (break/continue) # check in godot
    # duplicate-argument-name # check in godot
    # self-assigning-variable # check in godot
    # comparison-with-callable
    # duplicate-key # check in godot
    # expression-not-assigned # check in godot
    # unreachable # check in godot
    # using-constant-test # check in godot
    # comparison-with-itself # check in godot
    # extract-loads-to-preload
    'unnecessary-pass': None,
    # class checks
    'private-method-call': None,
    # useless-super-delegation
    'class-definitions-order': [
        'tools',
        'extends',
        'classnames',
        'enums',
        'consts',
        'signals',
        'exports',
        'onreadypubvars',
        'pubvars',
        'onreadyprvvars',
        'prvvars',
        'others',
    ],
    # design checks
    # max-locals
    # max-returns
    # max-branches
    # max-statements
    # max-attributes
    # max-public-methods
    # max-private-methods
    # max-nested-blocks
    'function-arguments-number': 10,
    # format checks
    'max-file-lines': 1000,
    # trailing-ws
    'max-line-length': 100,
    # misc
    # never-returning-function # for non-void, typed functions
    # simplify-boolean-expression
    # consider-using-in
    # inconsistent-return-statements
    # redefined-argument-from-local
    # chained-comparison
    # unused-load-const
    # unused-argument
    # unused-variable
    # pointless-statement
    # Constant actual parameter value
    # magic values
    # == on floats
    # misc-redundant-expression ~ https://clang.llvm.org/extra/clang-tidy/checks/misc-redundant-expression.html
    # readability-magic-numbers ~ https://clang.llvm.org/extra/clang-tidy/checks/readability-magic-numbers.html
    # bugprone-virtual-near-miss ~ https://clang.llvm.org/extra/clang-tidy/checks/list.html
})


def lint_code(gdscript_code, config=DEFAULT_CONFIG):
    disable = config['disable']
    parse_tree = parser_with_metadata_gathering.parse(gdscript_code)
    checks_to_run_w_tree = [
        (
            'function-arguments-number',
            partial(_function_args_num_check, config['function-arguments-number']),
        ),
    ]
    problem_clusters = map(
        lambda x: x[1](parse_tree) if x[0] not in disable else [], checks_to_run_w_tree
    )
    problems = [problem for cluster in problem_clusters for problem in cluster]
    checks_to_run_w_code = [
        (
            'max-line-length',
            partial(_max_line_length_check, config['max-line-length']),
        ),
        (
            'max-file-lines',
            partial(_max_file_lines_check, config['max-file-lines']),
        ),
    ]
    problem_clusters = map(
        lambda x: x[1](gdscript_code) if x[0] not in disable else [], checks_to_run_w_code
    )
    problems += [problem for cluster in problem_clusters for problem in cluster]
    problems += name_checks.lint(parse_tree, config)
    problems += class_checks.lint(parse_tree, config)
    problems += basic_checks.lint(parse_tree, config)
    return problems


def _function_args_num_check(threshold, parse_tree):
    problems = []
    for func_def in parse_tree.find_data('func_def'):
        func_name_token = func_def.children[0]
        assert func_name_token.type == 'NAME'
        func_name = func_name_token.value
        if len(func_def.children) == 1: # TODO: fix empty func parsing?
            continue
        if isinstance(func_def.children[1], Tree) and func_def.children[1].data == 'func_args':
            args_num = len(func_def.children[1].children)
            if args_num > threshold:
                problems.append(Problem(
                    name='function-arguments-number',
                    description='Function "{}" has more than {} arguments'.format(func_name, threshold),
                    line=func_name_token.line,
                    column=func_name_token.column,
                ))
    return problems


def _max_line_length_check(threshold, code):
    problems = []
    lines = code.split('\n')
    for line_number in range(len(lines)):
        if len(lines[line_number]) > threshold:
            problems.append(Problem(
                name='max-line-length',
                description='Max allowed line length ({}) exceeded'.format(threshold),
                line=line_number + 1,
                column=0,
            ))
    return problems


def _max_file_lines_check(threshold, code):
    problems = []
    lines = code.split('\n')
    if len(lines) > threshold:
        problems.append(Problem(
            name='max-file-lines',
            description='Max allowed file lines num ({}) exceeded'.format(threshold),
                line=len(lines),
                column=0,
            ))
    return problems
