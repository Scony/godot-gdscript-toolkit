import pytest

from gdtoolkit.parser import parser


@pytest.fixture(scope="session", autouse=True)
def disable_parser_caching():
    parser.disable_grammar_caching()
