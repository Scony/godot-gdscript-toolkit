from functools import partial

from lark import Tree

from .. import Problem


def lint(parse_tree, config):
    disable = config['disable']
    checks_to_run_w_tree = [
        (
            'unnecessary-pass',
            _unnecessary_pass_check,
        ),
    ]
    problem_clusters = map(
        lambda x: x[1](parse_tree) if x[0] not in disable else [], checks_to_run_w_tree
    )
    problems = [problem for cluster in problem_clusters for problem in cluster]
    return problems


def _unnecessary_pass_check(parse_tree): # performance... use AST once available
    problems = []
    for node in parse_tree.iter_subtrees():
        if isinstance(node, Tree):
            pass_stmts = _find_stmts_among_children(tree=node, suffix='pass_stmt')
            all_stmts = _find_stmts_among_children(tree=node, suffix='_stmt')
            if len(pass_stmts) < len(all_stmts):
                for pass_stmt in pass_stmts:
                    problems.append(Problem(
                        name='unnecessary-pass',
                        description='"pass" statement not necessary',
                        line=pass_stmt.line,
                        column=pass_stmt.column,
                    ))
    return problems


def _find_stmts_among_children(tree, suffix):
    stmts = []
    for child in tree.children:
        if isinstance(child, Tree):
            name = child.data
            if name.endswith(suffix):
                stmts.append(child)
    return stmts
