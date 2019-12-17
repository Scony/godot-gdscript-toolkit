from lark import Token

from .. import Problem


def lint(parse_tree, config):
    disable = config['disable']
    checks_to_run_w_tree = [
        (
            'private-method-call',
            _private_method_call_check,
        ),
    ]
    problem_clusters = map(
        lambda x: x[1](parse_tree) if x[0] not in disable else [], checks_to_run_w_tree
    )
    problems = [problem for cluster in problem_clusters for problem in cluster]
    return problems


def _private_method_call_check(parse_tree):
    problems = []
    for getattr_call in parse_tree.find_data('getattr_call'):
        _getattr = getattr_call.children[0]
        callee_name_token = _getattr.children[-1]
        callee_name = callee_name_token.value
        called = _getattr.children[-2]
        if isinstance(called, Token) and called.type == 'NAME' and called.value == 'self':
            continue
        if not is_method_private(callee_name):
            continue
        problems.append(Problem(
            name='private-method-call',
            description='Private method "{}" has been called'.format(callee_name),
            line=callee_name_token.line,
            column=callee_name_token.column,
        ))
    return problems


def is_method_private(method_name):
    return method_name.startswith('_') # TODO: consider making configurable
