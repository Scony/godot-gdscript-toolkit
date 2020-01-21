import os
import subprocess
import shutil

import pytest

from .common import format_and_compare


DATA_DIR = "./input-output-pairs"
GODOT_SERVER = "godot-server"
EXCEPTIONS = set(  # TODO: fix wherever possible
    [
        "simple-nested-class-stmts.out.gd",
        "comment-corner-case.out.gd",
        "simple-atom-expressions.in.gd",
        "force-multiline-dict.in.gd",
        "negation-n-bitwise-not-expressions.out.gd",
        "type-test-expressions.out.gd",
        "long-dict-expressions.in.gd",
        "type-cast-expressions.out.gd",
        "comment-corner-case.in.gd",
        "call-expressions.in.gd",
        "short-dict-expressions.out.gd",
        "type-test-expressions.in.gd",
        "simple-atom-expressions.out.gd",
        "class-stmt-chain.out.gd",
        "class-stmt-chain.in.gd",
        "short-dict-expressions.in.gd",
        "force-multiline-dict.out.gd",
        "simple-class-stmts.in.gd",
        "long-dict-expressions.out.gd",
        "type-cast-expressions.in.gd",
        "simple-class-stmts.out.gd",
        "simple-nested-class-stmts.in.gd",
        "call-expressions.out.gd",
        "negation-n-bitwise-not-expressions.in.gd",
        "simple-function-statements.in.gd",
        "simple-function-statements.out.gd",
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
