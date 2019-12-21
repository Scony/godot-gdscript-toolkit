from functools import partial

from lark import Tree

from .. import Problem


def lint(gdscript_code, parse_tree, config):
    disable = config['disable']
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
