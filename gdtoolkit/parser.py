import sys
import os
from pathlib import Path

from lark import Lark, indenter


class Indenter(indenter.Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = ['LPAR', 'LSQB', 'LBRACE']
    CLOSE_PAREN_types = ['RPAR', 'RSQB', 'RBRACE']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4                 # TODO: guess


_self_dir = os.path.dirname(os.path.abspath(Path(__file__).resolve()))

# fast parser, just for tree building and checking syntax
parser = Lark.open(
    os.path.join(_self_dir, 'gdscript.lark'),
    postlex=Indenter(),
    parser='lalr',
    start='start'
)

# slower parser, gathering metadata for static analysis
parser_with_metadata_gathering = Lark.open(
    os.path.join(_self_dir, 'gdscript.lark'),
    postlex=Indenter(),
    parser='lalr',
    start='start',
    propagate_positions=True
)
