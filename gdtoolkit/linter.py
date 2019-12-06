import re

from lark import Tree

from .parser import parser_with_metadata_gathering


class Problem:
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
    return _function_name_check(parse_tree) + _function_args_num_check(parse_tree)


def _function_name_check(parse_tree):
    problems = []
    func_name_regex = re.compile('[a-z_]+')
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


def _function_args_num_check(parse_tree): # TODO: consolidate
    problems = []
    for func_def in parse_tree.find_data('func_def'):
        THRESHOLD = 10
        func_name_token = func_def.children[0]
        assert func_name_token.type == 'NAME'
        func_name = func_name_token.value
        if isinstance(func_def.children[1], Tree) and func_def.children[1].data == 'func_args':
            args_num = len(func_def.children[1].children)
            if args_num > THRESHOLD:
                problems.append(Problem(
                    code='2',
                    name='function-arguments-number',
                    description='Function "{}" has more than {} arguments'.format(func_name, THRESHOLD),
                    line=func_name_token.line,
                    column=func_name_token.column,
                ))
    return problems
