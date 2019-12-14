import re
from functools import partial
from types import MappingProxyType

from lark import Tree, Token

from .parser import parser_with_metadata_gathering
from . import Problem

PASCAL_CASE = r'([A-Z][a-z0-9]*)+'
SNAKE_CASE = r'[a-z][a-z0-9]*(_[a-z0-9]+)*'
PRIVATE_SNAKE_CASE = r'_?{}'.format(SNAKE_CASE)
UPPER_SNAKE_CASE = r'[A-Z][A-Z0-9]*(_[A-Z0-9]+)*'

DEFAULT_CONFIG = MappingProxyType({
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
    'disable': [],
    # basic checks
    # not-in-loop (break/continue) # check in godot
    # duplicate-argument-name # check in godot
    # self-assigning-variable # check in godot
    # comparison-with-callable
    # duplicate-key # check in godot
    # expression-not-assigned # check in godot
    # unnecessary-pass # check in godot
    # unreachable # check in godot
    # using-constant-test # check in godot
    # comparison-with-itself # check in godot

    # class checks
    # protected-access
    # useless-super-delegation

    # design checks
    'function-arguments-number': 10,
    # max-locals
    # max-returns
    # max-branches
    # max-statements
    # max-attributes
    # max-public-methods
    # max-private-methods
    # max-nested-blocks
    # max-line-length
    # max-file-lines
    # trailing-ws

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
})


def lint_code(gdscript_code, config=DEFAULT_CONFIG):
    disable = config['disable']
    parse_tree = parser_with_metadata_gathering.parse(gdscript_code)
    rule_name_tokens = _gather_rule_name_tokens(parse_tree, [
        'class_def',
        'func_def',
        'classname_stmt',
        'signal_stmt',
        'enum_named',
        'enum_element',
        'for_stmt',
        'func_arg_regular',
        'func_arg_inf',
        'func_arg_typed',
    ])
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
    checks_to_run_wo_tree = [
        (
            'function-name',
            partial(
                _generic_name_check,
                config['function-name'],
                rule_name_tokens['func_def'],
                'function-name',
                'Function name "{}" is not valid',
            ),
        ),
        (
            'sub-class-name',
            partial(
                _generic_name_check,
                config['sub-class-name'],
                rule_name_tokens['class_def'],
                'sub-class-name',
                'Class name "{}" is not valid',
            ),
        ),
        (
            'class-name',
            partial(
                _generic_name_check,
                config['class-name'],
                rule_name_tokens['classname_stmt'],
                'class-name',
                'Class name "{}" is not valid',
            ),
        ),
        (
            'signal-name',
            partial(
                _generic_name_check,
                config['signal-name'],
                rule_name_tokens['signal_stmt'],
                'signal-name',
                'Signal name "{}" is not valid',
            ),
        ),
        (
            'enum-name',
            partial(
                _generic_name_check,
                config['enum-name'],
                rule_name_tokens['enum_named'],
                'enum-name',
                'Enum name "{}" is not valid',
            ),
        ),
        (
            'enum-element-name',
            partial(
                _generic_name_check,
                config['enum-element-name'],
                rule_name_tokens['enum_element'],
                'enum-element-name',
                'Enum element name "{}" is not valid',
            ),
        ),
        (
            'loop-variable-name',
            partial(
                _generic_name_check,
                config['loop-variable-name'],
                rule_name_tokens['for_stmt'],
                'loop-variable-name',
                'Loop variable name "{}" is not valid',
            ),
        ),
        (
            'function-argument-name',
            partial(
                _generic_name_check,
                config['function-argument-name'],
                rule_name_tokens['func_arg_regular'] +\
                rule_name_tokens['func_arg_inf'] +\
                rule_name_tokens['func_arg_typed'],
                'function-argument-name',
                'Function argument name "{}" is not valid',
            ),
        ),
        (
            'function-variable-name',
            partial(
                _generic_name_check,
                config['function-variable-name'],
                _gather_rule_name_tokens(
                    parse_tree,
                    ['func_var_stmt'],
                    lambda x: not _has_load_or_preload_call_expr(x),
                )['func_var_stmt'],
                'function-variable-name',
                'Function-scope variable name "{}" is not valid',
            ),
        ),
        (
            'function-load-variable-name',
            partial(
                _generic_name_check,
                config['function-load-variable-name'],
                _gather_rule_name_tokens(
                    parse_tree,
                    ['func_var_stmt'],
                    _has_load_or_preload_call_expr,
                )['func_var_stmt'],
                'function-load-variable-name',
                'Function-scope load/preload variable name "{}" is not valid',
            ),
        ),
        (
            'constant-name',
            partial(
                _generic_name_check,
                config['constant-name'],
                _gather_rule_name_tokens(
                    parse_tree,
                    ['const_stmt'],
                    lambda x: not _has_load_or_preload_call_expr(x),
                )['const_stmt'],
                'constant-name',
                'Constant name "{}" is not valid',
            ),
        ),
        (
            'load-constant-name',
            partial(
                _generic_name_check,
                config['load-constant-name'],
                _gather_rule_name_tokens(
                    parse_tree,
                    ['const_stmt'],
                    _has_load_or_preload_call_expr,
                )['const_stmt'],
                'load-constant-name',
                'Constant (load/preload) name "{}" is not valid',
            ),
        ),
        (
            'class-variable-name',
            partial(
                _generic_name_check,
                config['class-variable-name'],
                _gather_rule_name_tokens(
                    parse_tree,
                    ['class_var_stmt'],
                    lambda x: not _has_load_or_preload_call_expr(x),
                )['class_var_stmt'],
                'class-variable-name',
                'Class-scope variable name "{}" is not valid',
            ),
        ),
        (
            'class-load-variable-name',
            partial(
                _generic_name_check,
                config['class-load-variable-name'],
                _gather_rule_name_tokens(
                    parse_tree,
                    ['class_var_stmt'],
                    _has_load_or_preload_call_expr,
                )['class_var_stmt'],
                'class-load-variable-name',
                'Class-scope load/preload variable name "{}" is not valid',
            ),
        ),
    ]
    problem_clusters = map(lambda x: x[1]() if x[0] not in disable else [], checks_to_run_wo_tree)
    problems += [problem for cluster in problem_clusters for problem in cluster]
    return problems


def _function_args_num_check(threshold, parse_tree):
    problems = []
    for func_def in parse_tree.find_data('func_def'):
        func_name_token = func_def.children[0]
        assert func_name_token.type == 'NAME'
        func_name = func_name_token.value
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


def _generic_name_check(name_regex, name_tokens, problem_name, description_template):
    problems = []
    name_regex = re.compile(name_regex)
    for name_token in name_tokens:
        name = name_token.value
        if name_regex.fullmatch(name) is None:
            problems.append(Problem(
                name=problem_name,
                description=description_template.format(name),
                line=name_token.line,
                column=name_token.column,
            ))
    return problems


def _gather_rule_name_tokens(parse_tree, rules, predicate=lambda _: True):
    name_tokens_per_rule = {rule:[] for rule in rules}
    for node in parse_tree.iter_subtrees():
        if isinstance(node, Tree) and node.data in rules:
            rule_name = node.data
            name_token = _find_name_token(node)
            if name_token is None:
                name_token = _find_name_token(node.children[0])
                predicate_outcome = predicate(node.children[0])
            else:
                predicate_outcome = predicate(node)
            assert name_token is not None
            if predicate_outcome:
                name_tokens_per_rule[rule_name].append(name_token)
    return name_tokens_per_rule


def _find_name_token(tree):
    for child in tree.children:
        if isinstance(child, Token) and child.type == 'NAME':
            return child
    return None


def _has_load_or_preload_call_expr(tree):
    for child in tree.children:
        if isinstance(child, Tree) and child.data == 'expr':
            expr = child
            if len(expr.children) == 1 and isinstance(expr.children[0], Tree) and \
               expr.children[0].data == 'call_expr':
                call_expr = expr.children[0]
                name_token = _find_name_token(call_expr)
                if name_token is not None: # is a real call_expr, TODO: introduce invis proxy?
                    name = name_token.value
                    return name in ['load', 'preload']
    return False
