import os
import subprocess
import shutil

import pytest

from gdtoolkit.parser import parse


OK_DATA_DIR = "valid-gd-scripts"
NOK_DATA_DIR = "invalid-gd-scripts"
GODOT_SERVER = "godot-server"


def pytest_generate_tests(metafunc):
    if "gdscript_ok_path" in metafunc.fixturenames:
        metafunc.parametrize(
            "gdscript_ok_path",
            [os.path.join(OK_DATA_DIR, x) for x in os.listdir(OK_DATA_DIR)],
        )
    if "gdscript_nok_path" in metafunc.fixturenames:
        metafunc.parametrize(
            "gdscript_nok_path",
            [os.path.join(NOK_DATA_DIR, x) for x in os.listdir(NOK_DATA_DIR)],
        )


def test_parsing_success(gdscript_ok_path):
    with open(gdscript_ok_path, "r") as fh:
        code = fh.read()
        parse(code)  # just checking if not throwing


@pytest.mark.skipif(shutil.which(GODOT_SERVER) is None, reason="requires godot server")
def test_godot_check_only_success(gdscript_ok_path):
    process = subprocess.Popen([GODOT_SERVER, "--check-only", "-s", gdscript_ok_path])
    process.wait()
    assert process.returncode == 0


def test_parsing_failure(gdscript_nok_path):
    with open(gdscript_nok_path, "r") as fh:
        code = fh.read()
        try:
            parse(code)
        except:  # pylint: disable=bare-except
            return
        raise Exception("shall fail")


@pytest.mark.skipif(shutil.which(GODOT_SERVER) is None, reason="requires godot server")
def test_godot_check_only_failure(gdscript_nok_path):
    process = subprocess.Popen([GODOT_SERVER, "--check-only", "-s", gdscript_nok_path])
    process.wait()
    assert process.returncode != 0
