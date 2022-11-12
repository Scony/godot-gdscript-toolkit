import subprocess

from ..common import write_file


def test_cc_on_empty_file_succeeds(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "")
    outcome = subprocess.run(
        ["gdradon", "cc", dummy_file], check=False, capture_output=True
    )
    assert outcome.returncode == 0
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) == 0


def test_cc_on_file_with_single_function_succeeds(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "func foo(): pass\n")
    outcome = subprocess.run(
        ["gdradon", "cc", dummy_file], check=False, capture_output=True
    )
    assert outcome.returncode == 0
    assert len(outcome.stdout.decode().splitlines()) == 2
    assert len(outcome.stderr.decode().splitlines()) == 0
