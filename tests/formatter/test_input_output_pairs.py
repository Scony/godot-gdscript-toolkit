import os
import subprocess
import shutil

import pytest

from .common import format_and_compare


DATA_DIR = "./input-output-pairs"
GODOT_SERVER = "godot-server"
EXCEPTIONS = set(  # TODO: fix wherever possible
    [
        "call-expressions.in.gd",  # cannot provide callee definitions for now
        "call-expressions.out.gd",  # cannot provide callee definitions for now
        "force-multiline-dict.out.gd",  # godot bug
        "negation-n-bitwise-not-expressions.in.gd",  # Invalid operand ("Array") to unary operator "~"
        "negation-n-bitwise-not-expressions.out.gd",  # Invalid operand ("Array") to unary operator "~"
        "simple-function-statements.in.gd",  # break & continue in function scope
        "simple-function-statements.out.gd",  # break & continue in function scope
        "type-cast-expressions.in.gd",  # godot bug
        "type-cast-expressions.out.gd",  # godot bug
    ]
)


def pytest_generate_tests(metafunc):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    if "test_name" in metafunc.fixturenames:
        tests_in_dir = os.path.join(this_directory, DATA_DIR)
        metafunc.parametrize(
            "test_name", set(f.split(".")[0] for f in os.listdir(tests_in_dir)),
        )
    if "gdscript_path" in metafunc.fixturenames:
        directory_tests = os.path.join(this_directory, DATA_DIR)
        metafunc.parametrize(
            "gdscript_path",
            [f for f in os.listdir(directory_tests) if f not in EXCEPTIONS],
        )


def test_input_output_pair(test_name):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(this_dir, DATA_DIR, "{}.in.gd".format(test_name))
    output_file_path = os.path.join(this_dir, DATA_DIR, "{}.out.gd".format(test_name))
    with open(input_file_path, "r") as input_fh:
        with open(output_file_path, "r") as output_fh:
            input_code = input_fh.read()
            expected_output_code = output_fh.read()
            format_and_compare(input_code, expected_output_code)


@pytest.mark.skipif(shutil.which(GODOT_SERVER) is None, reason="requires godot server")
def test_script_is_valid(gdscript_path):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    directory_tests = os.path.join(this_directory, DATA_DIR)
    gdscript_full_path = os.path.join(directory_tests, gdscript_path)
    process = subprocess.Popen([GODOT_SERVER, "--check-only", "-s", gdscript_full_path])
    process.wait()
    assert process.returncode == 0
