import os
import subprocess
import shutil

import pytest

from gdtoolkit.parser import parser


OK_DATA_DIR = "./valid-gd-scripts"
NOK_DATA_DIR = "./invalid-gd-scripts"
BUGS_DATA_DIR = "./potential-godot-bugs"
GODOT_SERVER = "godot4"


def pytest_generate_tests(metafunc):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    if "gdscript_ok_path" in metafunc.fixturenames:
        directory_tests = os.path.join(this_directory, OK_DATA_DIR)
        metafunc.parametrize(
            "gdscript_ok_path",
            [os.path.join(directory_tests, f) for f in os.listdir(directory_tests)],
        )
    if "gdscript_nok_path" in metafunc.fixturenames:
        directory_tests = os.path.join(this_directory, NOK_DATA_DIR)
        metafunc.parametrize(
            "gdscript_nok_path",
            [os.path.join(directory_tests, f) for f in os.listdir(directory_tests)],
        )
    if "gdscript_bug_path" in metafunc.fixturenames:
        directory_tests = os.path.join(this_directory, BUGS_DATA_DIR)
        metafunc.parametrize(
            "gdscript_bug_path",
            [os.path.join(directory_tests, f) for f in os.listdir(directory_tests)],
        )


def test_parsing_success(gdscript_ok_path):
    with open(gdscript_ok_path, "r") as fh:
        code = fh.read()
        parser.parse(code)  # just checking if not throwing


@pytest.mark.skipif(shutil.which(GODOT_SERVER) is None, reason="requires godot server")
@pytest.mark.godot_check_only
def test_godot_check_only_success(gdscript_ok_path):
    process = subprocess.Popen(
        [GODOT_SERVER, "--headless", "--check-only", "-s", gdscript_ok_path],
        stderr=subprocess.PIPE,
    )
    process.wait()
    _, stderr = process.communicate()
    assert stderr == b""
    # TODO: fix once godot4 build is working
    # assert process.returncode == 0


def test_parsing_failure(gdscript_nok_path):
    with open(gdscript_nok_path, "r") as fh:
        code = fh.read()
        try:
            parser.parse(code)
        except:  # pylint: disable=bare-except
            return
        raise Exception("shall fail")


@pytest.mark.skipif(shutil.which(GODOT_SERVER) is None, reason="requires godot server")
@pytest.mark.godot_check_only
def test_godot_check_only_failure(gdscript_nok_path):
    process = subprocess.Popen(
        [GODOT_SERVER, "--headless", "--check-only", "-s", gdscript_nok_path],
        stderr=subprocess.PIPE,
    )
    process.wait()
    _, stderr = process.communicate()
    assert stderr != b""
    # TODO: fix once godot4 build is working
    # assert process.returncode != 0


@pytest.mark.skipif(shutil.which(GODOT_SERVER) is None, reason="requires godot server")
@pytest.mark.godot_check_only
def test_godot_check_only_potential_bugs(gdscript_bug_path):
    process = subprocess.Popen(
        [GODOT_SERVER, "--headless", "--check-only", "-s", gdscript_bug_path],
        stderr=subprocess.PIPE,
    )
    process.wait()
    _, stderr = process.communicate()
    assert stderr != b""
    # TODO: fix once godot4 build is working
    # assert process.returncode != 0
