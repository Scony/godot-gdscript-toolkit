import os

import difflib

from gdtoolkit.gd2py import convert_code


DATA_DIR = "./input-output-pairs"


def pytest_generate_tests(metafunc):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    if "test_name" in metafunc.fixturenames:
        tests_in_dir = os.path.join(this_directory, DATA_DIR)
        metafunc.parametrize(
            "test_name", set(f.split(".")[0] for f in os.listdir(tests_in_dir))
        )


def test_input_output_pair(test_name):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(this_dir, DATA_DIR, "{}.in.gd".format(test_name))
    output_file_path = os.path.join(this_dir, DATA_DIR, "{}.out.py".format(test_name))
    with open(input_file_path, "r", encoding="utf-8") as input_handle:
        with open(output_file_path, "r", encoding="utf-8") as output_handle:
            input_code = input_handle.read()
            expected_output_code = output_handle.read()
            _convert_and_compare(input_code, expected_output_code)


def _convert_and_compare(input_code, expected_output_code):
    converted_code = convert_code(input_code)
    _compare(converted_code, expected_output_code)


def _compare(input_code, expected_output_code):
    diff = "\n".join(
        difflib.unified_diff(expected_output_code.splitlines(), input_code.splitlines())
    )
    assert input_code == expected_output_code, diff
