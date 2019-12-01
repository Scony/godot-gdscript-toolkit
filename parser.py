#!/usr/bin/env python3

import sys
import os
from pathlib import Path

from lark import Lark
import lark.indenter

class Indenter(lark.indenter.Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = ['LPAR', 'LSQB', 'LBRACE']
    CLOSE_PAREN_types = ['RPAR', 'RSQB', 'RBRACE']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8

self_dir = os.path.dirname(os.path.abspath(Path(__file__).resolve()))
parser = Lark.open(os.path.join(self_dir, 'gdscript.lark'), postlex=Indenter(), parser='lalr')

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        with open(arg, 'r') as fh:
            content = fh.read()
            parser.parse(content)
