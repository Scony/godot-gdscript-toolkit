import re
from functools import partial

from lark import Tree, Token

from .parser import parser_with_metadata_gathering


DEFAULT_CONFIG = {
    'func-name-regex': r'[a-z_]+',
    'func-args-num-max': 10,
    'class-name-regex': r'([A-Z][a-z]*)+',
}


class Problem:                  # TODO: use dataclass if python 3.6 support is dropped
    def __init__(self, name: str, description: str, line: int, column: int):
        self.name = name
        self.description = description
        self.line = line
        self.column = column

    def __repr__(self):
        return 'Problem({})'.format({
            'name': self.name,
            'description': self.description,
            'line': self.line,
            'column': self.column,
        })


def lint_code(gdscript_code):
    parse_tree = parser_with_metadata_gathering.parse(gdscript_code)
    rule_name_tokens = _gather_rule_name_tokens(parse_tree, [
        'class_def',
        'func_def',
    ])
    checks_to_run_w_tree = [
        partial(_function_args_num_check, DEFAULT_CONFIG['func-args-num-max']),
    ]
    problem_clusters = map(lambda f: f(parse_tree), checks_to_run_w_tree)
    problems = [problem for cluster in problem_clusters for problem in cluster]
    checks_to_run_wo_tree = [
        partial(_class_name_check, DEFAULT_CONFIG['class-name-regex'], rule_name_tokens['class_def']),
        partial(_function_name_check, DEFAULT_CONFIG['func-name-regex'], rule_name_tokens['func_def']),
    ]
    problem_clusters = map(lambda f: f(), checks_to_run_wo_tree)
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


def _function_name_check(func_name_regex, func_name_tokens):
    problems = []
    func_name_regex = re.compile(func_name_regex)
    for func_name_token in func_name_tokens:
        assert func_name_token.type == 'NAME'
        func_name = func_name_token.value
        if func_name_regex.match(func_name) is None:
            problems.append(Problem(
                name='function-name',
                description='Function name "{}" is not valid'.format(func_name),
                line=func_name_token.line,
                column=func_name_token.column,
            ))
    return problems


def _class_name_check(class_name_regex, class_name_tokens):
    problems = []
    class_name_regex = re.compile(class_name_regex)
    for class_name_token in class_name_tokens:
        class_name = class_name_token.value
        if class_name_regex.match(class_name) is None:
            problems.append(Problem(
                name='class-name',
                description='Class name "{}" is not valid'.format(class_name),
                line=class_name_token.line,
                column=class_name_token.column,
            ))
    return problems


def _gather_rule_name_tokens(parse_tree, rules):
    name_tokens_per_rule = {rule:[] for rule in rules}
    for node in parse_tree.iter_subtrees():
        if isinstance(node, Tree) and node.data in rules:
            rule_name = node.data
            name_token = _find_name_token(node)
            assert name_token is not None
            name_tokens_per_rule[rule_name].append(name_token)
    return name_tokens_per_rule


def _find_name_token(tree):
    for child in tree.children:
        if isinstance(child, Token) and child.type == 'NAME':
            return child
    return None
