import os
import subprocess
import shutil

import pytest


DATA_DIR = "./input-output-pairs"
GODOT_SERVER = "godot4"
EXCEPTIONS = set(
    [
        "if-corner-case.in.gd",
        "if-corner-case.out.gd",
        # TODO:
        "simple-match-statements.in.gd",
        "simple-match-statements.out.gd",
        # complex expressions where Godot does more than just parsing
        "type-cast-corner-case-expressions.in.gd",
        "type-cast-corner-case-expressions.out.gd",
        # godot bugs:
        "complex-trailing-comma-scenarios.in.gd",
        "complex-trailing-comma-scenarios.out.gd",
    ]
)


def pytest_generate_tests(metafunc):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    if "gdscript_path" in metafunc.fixturenames:
        directory_tests = os.path.join(this_directory, DATA_DIR)
        metafunc.parametrize(
            "gdscript_path",
            [f for f in os.listdir(directory_tests) if f not in EXCEPTIONS],
        )


@pytest.mark.skipif(shutil.which(GODOT_SERVER) is None, reason="requires godot server")
@pytest.mark.godot_check_only
def test_script_is_valid(gdscript_path):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    directory_tests = os.path.join(this_directory, DATA_DIR)
    gdscript_full_path = os.path.join(directory_tests, gdscript_path)
    process = subprocess.Popen(
        [GODOT_SERVER, "--headless", "--check-only", "-s", gdscript_full_path],
    )
    process.wait()
    assert process.returncode == 0
