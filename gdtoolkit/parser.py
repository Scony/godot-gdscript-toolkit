import os
from pathlib import Path

from lark import Lark, indenter, Tree


SELF_DIR = os.path.dirname(os.path.abspath(Path(__file__).resolve()))


def parse(
    code: str, gather_metadata: bool = False
) -> Tree:  # TODO: lazy parser loading
    """gdscript parsing function - when gather_metadata is True
       the parsing will be slower but the tree will contain metadata
       like line and column positions for rules and tokens"""
    global _parser, _parser_with_metadata_gathering
    code += "\n"
    if gather_metadata:
        if _parser_with_metadata_gathering is None:
            _parser_with_metadata_gathering = Lark.open(
                os.path.join(SELF_DIR, "gdscript.lark"),
                postlex=Indenter(),
                parser="lalr",
                start="start",
                propagate_positions=True,
            )
        return _parser_with_metadata_gathering.parse(code)
    if _parser is None:
        _parser = Lark.open(
            os.path.join(SELF_DIR, "gdscript.lark"),
            postlex=Indenter(),
            parser="lalr",
            start="start",
        )
    return _parser.parse(code)


class Indenter(indenter.Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4  # TODO: guess


_parser = None
_parser_with_metadata_gathering = None
