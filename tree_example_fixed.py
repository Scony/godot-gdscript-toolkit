from lark import Lark
from lark.indenter import Indenter

tree_grammar = r"""
start: (_NL | stmt)*
stmt: cx_stmt | (sm_stmt _NL)
sm_stmt: NAME
stmt_chain: stmt* [sm_stmt]
cx_stmt: NAME ":" _NL _INDENT stmt_chain _DEDENT
%import common.CNAME -> NAME
%declare _INDENT _DEDENT
_NL: /(\r?\n[\t ]*)+/
"""

class TreeIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8

parser = Lark(tree_grammar, parser='lalr', postlex=TreeIndenter())

test_tree = """
a:
    b
    c:
        d
        e
    f:
        g
    h:
        i"""

def test():
    print(parser.parse(test_tree).pretty())
    print(parser.parse(test_tree))

if __name__ == '__main__':
    test()
