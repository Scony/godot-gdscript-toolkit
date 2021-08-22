import pytest

from gdtoolkit.parser import parser


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "godot_check_only: testcase uses headless godot w/ --check-only"
    )


@pytest.fixture(scope="session", autouse=True)
def disable_parser_caching():
    parser.disable_grammar_caching()
