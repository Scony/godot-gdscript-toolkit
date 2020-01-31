"""
Initializes and caches the GDScript parsers, using Lark.
Provides a function to parse GDScript code
and to get an intermediate representation as a Lark Tree.
"""
import os
import re

from lark import Lark, Tree, indenter


class Indenter(indenter.Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    # TODO: guess tab length
    tab_len = 4


# When upgrading to Python 3.8, replace with functools.cached_property
class cached_property:
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property.
        """

    def __init__(self, func):
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class Parser:
    """Parses GDScript code using lark parsers.
    The parsers are only created once, upon using them for the first time.
    """

    def __init__(self):
        self._directory = os.path.dirname(__file__)

    def parse(
        self, code: str, gather_metadata: bool = False, loosen_grammar: bool = False
    ) -> Tree:
        """Parses GDScript code and returns an intermediate representation as a Lark Tree.
        If gather_metadata is True, parsing is slower but the returned Tree comes with
        line and column numbers for statements and rules.
        """
        code += "\n"  # to overcome lark bug (#489)
        if loosen_grammar:
            return self._loosen_parser_with_metadata.parse(code)
        return (
            self._parser_with_metadata.parse(code)
            if gather_metadata
            else self._parser.parse(code)
        )

    @cached_property
    def _parser(self) -> Tree:
        return Lark.open(
            os.path.join(self._directory, "gdscript.lark"),
            postlex=Indenter(),
            parser="lalr",
            start="start",
            maybe_placeholders=False,
        )

    @cached_property
    def _parser_with_metadata(self) -> Tree:
        return Lark.open(
            os.path.join(self._directory, "gdscript.lark"),
            postlex=Indenter(),
            parser="lalr",
            start="start",
            propagate_positions=True,
            maybe_placeholders=False,
        )

    @cached_property
    def _loosen_parser_with_metadata(self) -> Tree:
        with open(os.path.join(self._directory, "gdscript.lark"), "r") as fh:
            grammar_code = fh.read()
            grammar_lines = grammar_code.splitlines()
            grammar_code = "\n".join(
                [re.sub(r"^!", "", line) for line in grammar_lines]
            )
            grammar_code = grammar_code.replace(" -> par_expr", "")
            return Lark(
                grammar_code,
                postlex=Indenter(),
                parser="lalr",
                start="start",
                propagate_positions=True,
                maybe_placeholders=False,
            )


parser = Parser()
