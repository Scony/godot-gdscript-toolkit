import subprocess

from ..common import write_file


def test_parsing_valid_file_succeeds(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    outcome = subprocess.run(["gdparse", dummy_file], check=False, capture_output=True)
    assert outcome.returncode == 0
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) == 0


def test_parsing_valid_files_succeeds(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    dummy_file2 = write_file(tmp_path, "script2.gd", "pass;pass")
    outcome = subprocess.run(
        ["gdparse", dummy_file, dummy_file2], check=False, capture_output=True
    )
    assert outcome.returncode == 0
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) == 0


def test_pretty_printing_valid_files_succeeds(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    dummy_file2 = write_file(tmp_path, "script2.gd", "pass;pass")
    outcome = subprocess.run(
        ["gdparse", "-p", dummy_file, dummy_file2], check=False, capture_output=True
    )
    assert outcome.returncode == 0
    assert len(outcome.stdout.decode().splitlines()) > 0
    assert len(outcome.stderr.decode().splitlines()) == 0


def test_pretty_printing_missing_file():
    outcome = subprocess.run(
        ["gdparse", "nonexistent.gd"], check=False, capture_output=True
    )
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_pretty_printing_unexpected_token():
    outcome = subprocess.run(
        ["gdparse", "-"], input=b"pass x", check=False, capture_output=True
    )
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_pretty_printing_lark_corner_case():
    code = b"""
func args(a, b):
	print(a)
	print(b)

func test():
	args(1,2"""
    outcome = subprocess.run(
        ["gdparse", "-"], input=code, check=False, capture_output=True
    )
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) > 0
