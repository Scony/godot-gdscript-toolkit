import subprocess

from ..common import write_file


def test_parsing_valid_file_succeeds(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "tool")
    outcome = subprocess.run(["gdparse", dummy_file], check=False, capture_output=True)
    assert outcome.returncode == 0
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) == 0


def test_pretty_printing_missing_file():
    outcome = subprocess.run(
        ["gdparse", "nonexistent.gd"], check=False, capture_output=True
    )
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) == 1
