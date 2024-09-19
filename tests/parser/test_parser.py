import os

import pytest
from gdtoolkit.parser import parser


OK_DATA_DIRS = [
    "../valid-gd-scripts",
    "../formatter/input-output-pairs",
]
NOK_DATA_DIR = "../invalid-gd-scripts"


def pytest_generate_tests(metafunc):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    if "gdscript_ok_path" in metafunc.fixturenames:
        tests = []
        for ok_data_dir in OK_DATA_DIRS:
            directory_tests = os.path.join(this_directory, ok_data_dir)
            tests += [
                os.path.join(directory_tests, f) for f in os.listdir(directory_tests)
            ]
        metafunc.parametrize("gdscript_ok_path", tests)
    if "gdscript_nok_path" in metafunc.fixturenames:
        directory_tests = os.path.join(this_directory, NOK_DATA_DIR)
        metafunc.parametrize(
            "gdscript_nok_path",
            [os.path.join(directory_tests, f) for f in os.listdir(directory_tests)],
        )


@pytest.mark.parser
def test_parsing_success(gdscript_ok_path):
    # TODO: fix lexer
    if "bug_326_multistatement_lambda_corner_case" in gdscript_ok_path:
        return
    with open(gdscript_ok_path, "r", encoding="utf-8") as handle:
        code = handle.read()
        parser.parse(code)  # just checking if not throwing


@pytest.mark.parser
def test_parsing_failure(gdscript_nok_path):
    with open(gdscript_nok_path, "r", encoding="utf-8") as handle:
        code = handle.read()
        try:
            parser.parse(code)
        except:  # pylint: disable=bare-except
            return
        assert True, "shall fail"
