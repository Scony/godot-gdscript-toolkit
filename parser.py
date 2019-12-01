import sys

from lark import Lark
import lark.indenter

class Indenter(lark.indenter.Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = ['LPAR', 'LSQB', 'LBRACE']
    CLOSE_PAREN_types = ['RPAR', 'RSQB', 'RBRACE']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8

parser = Lark.open('gdscript.lark', postlex=Indenter(), parser='lalr')

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        with open(arg, 'r') as fh:
            content = fh.read()
            parser.parse(content)
