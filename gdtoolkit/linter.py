import re
from functools import partial

from lark import Tree

from .parser import parser_with_metadata_gathering


DEFAULT_CONFIG = {
    'func-name-regex': r'[a-z_]+',
    'func-args-num-max': 10,
    'class-name-regex': r'([A-Z][a-z]*)+',
}


class Problem:                  # TODO: use dataclass if python 3.6 support is dropped
    def __init__(self, code: str, name: str, description: str, line: int, column: int):
        self.code = code
        self.name = name
        self.description = description
        self.line = line
        self.column = column

    def __repr__(self):
        return 'Problem({})'.format({
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'line': self.line,
            'column': self.column,
        })


def lint_code(gdscript_code):
    parse_tree = parser_with_metadata_gathering.parse(gdscript_code)
    checks_to_run = [
        partial(_function_name_check, DEFAULT_CONFIG['func-name-regex']),
        partial(_function_args_num_check, DEFAULT_CONFIG['func-args-num-max']),
        partial(_class_name_check, DEFAULT_CONFIG['class-name-regex']),
    ]
    problem_clusters = map(lambda f: f(parse_tree), checks_to_run)
    return [problem for cluster in problem_clusters for problem in cluster]


def _function_name_check(func_name_regex, parse_tree):
    problems = []
    func_name_regex = re.compile(func_name_regex)
    for func_def in parse_tree.find_data('func_def'):
        func_name_token = func_def.children[0]
        assert func_name_token.type == 'NAME'
        func_name = func_name_token.value
        if func_name_regex.match(func_name) is None:
            problems.append(Problem(
                code='1',
                name='function-name',
                description='Function name "{}" is not valid'.format(func_name),
                line=func_name_token.line,
                column=func_name_token.column,
            ))
    return problems


def _function_args_num_check(threshold, parse_tree): # TODO: consolidate
    problems = []
    for func_def in parse_tree.find_data('func_def'):
        func_name_token = func_def.children[0]
        assert func_name_token.type == 'NAME'
        func_name = func_name_token.value
        if isinstance(func_def.children[1], Tree) and func_def.children[1].data == 'func_args':
            args_num = len(func_def.children[1].children)
            if args_num > threshold:
                problems.append(Problem(
                    code='2',
                    name='function-arguments-number',
                    description='Function "{}" has more than {} arguments'.format(func_name, threshold),
                    line=func_name_token.line,
                    column=func_name_token.column,
                ))
    return problems


def _class_name_check(class_name_regex, parse_tree): # TODO: consolidate
    problems = []
    class_name_regex = re.compile(class_name_regex)
    for class_def in parse_tree.find_data('class_def'):
        class_name_token = class_def.children[0]
        assert class_name_token.type == 'NAME'
        class_name = class_name_token.value
        if class_name_regex.match(class_name) is None:
            problems.append(Problem(
                code='1',
                name='class-name',
                description='Class name "{}" is not valid'.format(class_name),
                line=class_name_token.line,
                column=class_name_token.column,
            ))
    return problems
