import sys


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


def print_problem(problem, file_path, file_lines, colorful=False): # TODO: colors
    print('{}:{}: Error: {} ({})'.format(
        file_path,
        problem.line,
        problem.description,
        problem.name,
    ), file=sys.stderr)
    # print(file_lines[problem.line-1], file=sys.stderr)
    # print('{}^'.format(' ' * problem.column)) # TODO: underline range instead
