"""
Initializes and caches the GDScript parsers, using Lark.
Provides a function to parse GDScript code
and to get an intermediate representation as a Lark Tree.
"""
import os
import pickle
import re
from typing import List

from lark import Lark, Tree, indenter
from lark.grammar import Rule
from lark.lexer import TerminalDef


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
        self._cache_dirpath: str = os.path.join(
            os.path.expanduser("~"), ".cache/gdtoolkit"
        )

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

    def parse_comments(self, code: str) -> Tree:
        """Parses GDScript code and returns comments - both standalone, and inline."""
        code += "\n"  # to overcome lark bug (#489)
        return self._comment_parser.parse(code)

    def _get_parser(
        self,
        name: str,
        add_metadata: bool = False,
        grammar_filename: str = "gdscript.lark",
        is_loosened_parser: bool = False,
    ) -> Tree:
        version = "3.2.5"

        tree: Tree = None
        filepath: str = os.path.join(self._cache_dirpath, version, name) + ".pickle"
        if not os.path.exists(filepath):
            # TODO: remove loosened parser, see #63
            #
            # This is a special parser to work around issues with trailing
            # commas in enums, etc.
            loosened_grammar_file = tempfile.TemporaryFile("w")
            if is_loosened_parser:
                with open(
                    os.path.join(self._directory, "gdscript.lark"), "r"
                ) as file_grammar:
                    grammar_lines: List[str] = file_grammar.read().splitlines()
                    grammar: str = "\n".join(
                        [re.sub(r"^!", "", line) for line in grammar_lines]
                    )
                    grammar = grammar.replace(" -> par_expr", "")
                    loosened_grammar_file.write(grammar)

            grammar: str = (
                loosened_grammar_file
                if is_loosened_parser
                else os.path.join(self._directory, grammar_filename)
            )
            tree = Lark.open(
                grammar,
                parser="lalr",
                start="start",
                postlex=Indenter(),
                propagate_positions=add_metadata,
                maybe_placeholders=False,
            )
            self.save(tree, filepath)
            loosened_grammar_file.close()
        tree = self.load(filepath)
        return tree

    @cached_property
    def _parser(self) -> Tree:
        return self._get_parser("parser")

    @cached_property
    def _parser_with_metadata(self) -> Tree:
        return self._get_parser("parser_with_metadata", True)

    # TODO: remove loosened parser, see #63
    @cached_property
    def _loosen_parser_with_metadata(self) -> Tree:
        return self._get_parser("loosened_parser_with_metadata", True)
        return

    @cached_property
    def _comment_parser(self) -> Tree:
        return self._get_parser("parser_comments", True, "comments.lark")

    def save(self, parser: Tree, path: str) -> None:
        """Serializes the Lark parser and saves it to the disk."""

        data, memo = parser.memo_serialize([TerminalDef, Rule])
        write_data: dict = {
            "data": data,
            "memo": memo,
        }

        dirpath: str = os.path.dirname(path)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        with open(path, "wb") as file_parser:
            pickle.dump(write_data, file_parser, pickle.HIGHEST_PROTOCOL)

    def load(self, path: str) -> Tree:
        """Loads the Lark parser from the disk and deserializes it."""
        with open(path, "rb") as file_parser:
            data: dict = pickle.load(file_parser)
            namespace = {"Rule": Rule, "TerminalDef": TerminalDef}
            return Lark.deserialize(
                data["data"],
                namespace,
                data["memo"],
                transformer=None,
                postlex=Indenter(),
            )


parser = Parser()
