import re

from .parser import parser_with_metadata_gathering


class Problem:
    def __init__(self, code: str, name: str, description: str, line: int, column: int):
        self.code = code
        self.name = name
        self.description = description
        self.line = line
        self.column = column


def function_name_check(parse_tree):
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


def lint_code(gdscript_code):
    parse_tree = parser_with_metadata_gathering.parse(gdscript_code)
    return function_name_check(parse_tree)
