import subprocess

from ..common import write_file


def test_valid_file(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "tool")
    assert subprocess.run(["gdformat", dummy_file], check=False).returncode == 0


def test_check_valid_file_unchanged(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "tool\n")
    assert (
        subprocess.run(["gdformat", "--check", dummy_file], check=False).returncode == 0
    )


def test_check_valid_file_to_reformat(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "tool;var x")
    assert (
        subprocess.run(["gdformat", "--check", dummy_file], check=False).returncode != 0
    )


def test_invalid_file(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "too")
    assert subprocess.run(["gdformat", dummy_file], check=False).returncode != 0


def test_invalid_file_check(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "too")
    assert (
        subprocess.run(["gdformat", "--check", dummy_file], check=False).returncode != 0
    )
