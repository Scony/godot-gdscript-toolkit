import subprocess

from ..common import write_file


def test_valid_file_no_config(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "tool")
    assert subprocess.run(["gdlint", dummy_file], check=False).returncode == 0


def test_valid_file_w_config(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "tool")
    assert subprocess.run(["gdlint", "-d"], cwd=tmp_path, check=False).returncode == 0
    assert (
        subprocess.run(["gdlint", dummy_file], cwd=tmp_path, check=False).returncode
        == 0
    )


def test_invalid_file_no_config(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "var Xx = 1")
    assert subprocess.run(["gdlint", dummy_file], check=False).returncode != 0


def test_invalid_file_w_config(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "var Xx = 1")
    assert subprocess.run(["gdlint", "-d"], cwd=tmp_path, check=False).returncode == 0
    assert (
        subprocess.run(["gdlint", dummy_file], cwd=tmp_path, check=False).returncode
        != 0
    )
