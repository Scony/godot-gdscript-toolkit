import os
import subprocess
import shutil

import pytest

from ..common import GODOT_SERVER, write_project_settings, write_file


OK_DATA_DIR = "../valid-gd-scripts"
NOK_DATA_DIR = "../invalid-gd-scripts"
BUGS_DATA_DIR = "../potential-godot-bugs"


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


@pytest.mark.skipif(shutil.which(GODOT_SERVER) is None, reason="requires godot server")
@pytest.mark.godot_check_only
def test_godot_check_only_success(gdscript_ok_path, tmp_path):
    write_project_settings(tmp_path)
    write_file(tmp_path, "dummy.gd", "class X:\n\tpass")
    with subprocess.Popen(
        [
            GODOT_SERVER,
            "--headless",
            "--check-only",
            "-s",
            gdscript_ok_path,
            "--path",
            tmp_path,
        ],
    ) as process:
        process.wait()
        assert process.returncode == 0


@pytest.mark.skipif(shutil.which(GODOT_SERVER) is None, reason="requires godot server")
@pytest.mark.godot_check_only
def test_godot_check_only_failure(gdscript_nok_path):
    with subprocess.Popen(
        [GODOT_SERVER, "--headless", "--check-only", "-s", gdscript_nok_path],
    ) as process:
        process.wait()
        assert process.returncode != 0


@pytest.mark.skipif(shutil.which(GODOT_SERVER) is None, reason="requires godot server")
@pytest.mark.godot_check_only
def test_godot_check_only_potential_bugs(gdscript_bug_path):
    with subprocess.Popen(
        [GODOT_SERVER, "--headless", "--check-only", "-s", gdscript_bug_path],
    ) as process:
        process.wait()
        assert process.returncode != 0
