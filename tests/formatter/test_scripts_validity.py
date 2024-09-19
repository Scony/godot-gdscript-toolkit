import os
import subprocess
import shutil

import pytest

from ..common import GODOT_SERVER, write_project_settings, write_file


DATA_DIR = "./input-output-pairs"
EXCEPTIONS = set(
    [
        # Godot bugs:
        "bug_326_multistatement_lambda_corner_case.out.gd",
        # cases where Godot does more than just parsing
        "inline_lambdas_w_comments.in.gd",
        "inline_lambdas_w_comments.out.gd",
        "long_inline_lambdas.in.gd",
        "long_inline_lambdas.out.gd",
        "type_cast_corner_case_expressions.in.gd",
        "type_cast_corner_case_expressions.out.gd",
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
def test_script_is_valid(gdscript_path, tmp_path):
    write_project_settings(tmp_path)
    write_file(tmp_path, "dummy.gd", "class X:\n\tpass")
    this_directory = os.path.dirname(os.path.abspath(__file__))
    directory_tests = os.path.join(this_directory, DATA_DIR)
    gdscript_full_path = os.path.join(directory_tests, gdscript_path)
    with subprocess.Popen(
        [
            GODOT_SERVER,
            "--headless",
            "--check-only",
            "-s",
            gdscript_full_path,
            "--path",
            tmp_path,
        ],
    ) as process:
        process.wait()
        assert process.returncode == 0
