"""
Initializes and caches the GDScript parsers, using Lark.
Provides a function to parse GDScript code
and to get an intermediate representation as a Lark Tree.
"""
import os
import sys
import pkg_resources

from lark import Lark, Tree

from .gdscript_indenter import GDScriptIndenter


# TODO: when upgrading to Python 3.8, replace with functools.cached_property
# pylint: disable=too-few-public-methods
class CachedProperty:
    """A property that is only computed once per instance and then replaces
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
        self._use_grammar_cache = True
        self._cache_dirpath: str = os.path.join(get_cache_directory(), "gdtoolkit")

    def parse(self, code: str, gather_metadata: bool = False) -> Tree:
        """Parses GDScript code and returns intermediate representation as a Lark Tree.
        If gather_metadata is True, parsing is slower but the returned Tree comes with
        line and column numbers for statements and rules.
        """
        # adding newline at the end of code
        # workarounds a few corner cases not addressed in the grammar
        adjusted_code = code + "\n"
        # pylint: disable=no-member
        return (
            self._parser_with_metadata.parse(adjusted_code)
            if gather_metadata
            else self._parser.parse(adjusted_code)
        )

    def parse_comments(self, code: str) -> Tree:
        """Parses GDScript code and returns comments - both standalone, and inline."""
        # pylint: disable=no-member
        return self._comment_parser.parse(code)

    def disable_grammar_caching(self) -> None:
        self._use_grammar_cache = False

    def _get_parser(
        self,
        name: str,
        add_metadata: bool = False,
        grammar_filename: str = "gdscript.lark",
    ) -> Lark:
        version: str = pkg_resources.get_distribution("gdtoolkit").version
        cache_dirpath: str = os.path.join(self._cache_dirpath, version)
        cache_filepath: str = os.path.join(cache_dirpath, name) + ".pickle"
        grammar_filepath: str = os.path.join(self._directory, grammar_filename)

        # TODO: catch IO exception
        if not os.path.exists(cache_dirpath):
            os.makedirs(cache_dirpath)

        # TODO: catch IO exception
        a_parser = Lark.open(
            grammar_filepath,
            parser="lalr",
            start="start",
            postlex=GDScriptIndenter(),  # type: ignore
            propagate_positions=add_metadata,
            maybe_placeholders=False,
            cache=cache_filepath,
            regex=True,
        )

        return a_parser

    @CachedProperty
    def _parser(self) -> Lark:
        return self._get_parser("parser")

    @CachedProperty
    def _parser_with_metadata(self) -> Lark:
        return self._get_parser("parser_with_metadata", add_metadata=True)

    @CachedProperty
    def _comment_parser(self) -> Lark:
        return self._get_parser(
            "parser_comments", add_metadata=True, grammar_filename="comments.lark"
        )


def get_cache_directory() -> str:
    """Returns the cache directory based on the user's operating system"""
    directory: str = ""
    if sys.platform in ["linux", "linux2"]:
        directory = os.path.join(os.path.expanduser("~"), ".cache")
    elif sys.platform == "darwin":
        directory = os.path.join(os.path.expanduser("~"), "Library", "Caches")
    elif sys.platform == "win32":
        directory = os.path.expandvars(r"%LOCALAPPDATA%")
    return directory


parser = Parser()
