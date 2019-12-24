import sys
from dataclasses import dataclass


@dataclass
class Problem:
    name: str
    description: str
    line: int
    column: int


def print_problem(problem, file_path):  # TODO: colors
    print(
        "{}:{}: Error: {} ({})".format(
            file_path, problem.line, problem.description, problem.name,
        ),
        file=sys.stderr,
    )
    # print(file_lines[problem.line-1], file=sys.stderr)
    # print('{}^'.format(' ' * problem.column)) # TODO: underline range instead
