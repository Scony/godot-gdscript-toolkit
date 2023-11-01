import os

from gdtoolkit.linter import lint_code

DATA_DIR = "../valid-gd-scripts"


def pytest_generate_tests(metafunc):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    if "gdscript_file_path" in metafunc.fixturenames:
        directory_tests = os.path.join(this_directory, DATA_DIR)
        metafunc.parametrize(
            "gdscript_file_path",
            [os.path.join(directory_tests, f) for f in os.listdir(directory_tests)],
        )


def test_linting_success(gdscript_file_path):
    with open(gdscript_file_path, "r", encoding="utf-8") as handle:
        code = handle.read()
        lint_code(code)  # just checking if not throwing
