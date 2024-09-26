import os

from gdtoolkit.gd2py import convert_code


VALID_SCRIPT_DIRS = [
    "../formatter/big-input-files",
    "../formatter/input-output-pairs",
    "../valid-gd-scripts",
]
EXCEPTIONS = [
    "bug_326_multistatement_lambda_corner_case.out.gd",
]


def pytest_generate_tests(metafunc):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    if "gdscript_path" in metafunc.fixturenames:
        valid_script_paths = set()
        for directory_relative_path in VALID_SCRIPT_DIRS:
            directory_absolute_path = os.path.join(
                this_directory, directory_relative_path
            )
            valid_script_paths = valid_script_paths.union(
                set(
                    os.path.join(directory_absolute_path, f)
                    for f in os.listdir(directory_absolute_path)
                )
            )
        metafunc.parametrize("gdscript_path", valid_script_paths)


def test_conversion_success(gdscript_path):
    if any(exception in gdscript_path for exception in EXCEPTIONS):
        return
    with open(gdscript_path, "r", encoding="utf-8") as file_handle:
        code = file_handle.read()
        convert_code(code)
