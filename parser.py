from lark import Lark
import lark.indenter

class Indenter(lark.indenter.Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8

parser = Lark.open('gdscript.lark', postlex=Indenter(), parser='lalr')

with open('scripts/recursive_tool.gd', 'r') as fh:
    content = fh.read()
    print(parser.parse(content).pretty())
