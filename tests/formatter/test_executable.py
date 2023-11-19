import subprocess

from ..common import write_file


def test_valid_file_formatting(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    outcome = subprocess.run(["gdformat", dummy_file], check=False, capture_output=True)
    assert outcome.returncode == 0, outcome.stderr.decode()
    assert len(outcome.stdout.decode().splitlines()) == 2
    assert len(outcome.stderr.decode().splitlines()) == 0


def test_valid_files_formatting(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    dummy_file_2 = write_file(tmp_path, "script2.gd", "pass;pass")
    outcome = subprocess.run(
        ["gdformat", dummy_file, dummy_file_2], check=False, capture_output=True
    )
    assert outcome.returncode == 0
    assert len(outcome.stdout.decode().splitlines()) == 3
    assert len(outcome.stderr.decode().splitlines()) == 0


def test_valid_files_formatting_with_nonexistent_one_keepgoing(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    dummy_file_3 = write_file(tmp_path, "script3.gd", "pass;pass")
    outcome = subprocess.run(
        ["gdformat", dummy_file, "nonexistent.gd", dummy_file_3],
        check=False,
        capture_output=True,
    )
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 3
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_valid_files_formatting_with_invalid_one_keepgoing(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    dummy_file_2 = write_file(tmp_path, "script2.gd", "pass x")  # invalid
    dummy_file_3 = write_file(tmp_path, "script3.gd", "pass;pass")
    outcome = subprocess.run(
        ["gdformat", dummy_file, dummy_file_2, dummy_file_3],
        check=False,
        capture_output=True,
    )
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 3
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_valid_formatted_file_checking(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass\n")
    outcome = subprocess.run(
        ["gdformat", "--check", dummy_file], check=False, capture_output=True
    )
    assert outcome.returncode == 0
    assert len(outcome.stdout.decode().splitlines()) == 1
    assert len(outcome.stderr.decode().splitlines()) == 0


def test_valid_unformatted_file_checking(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass;var x")
    outcome = subprocess.run(
        ["gdformat", "--check", dummy_file], check=False, capture_output=True
    )
    assert outcome.returncode != 0
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) == 2


def test_valid_unformatted_files_checking_with_invalid_one_keepgoing(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    dummy_file_2 = write_file(tmp_path, "script2.gd", "pass x")  # invalid
    dummy_file_3 = write_file(tmp_path, "script3.gd", "pass;pass")
    outcome = subprocess.run(
        ["gdformat", "--check", dummy_file, dummy_file_2, dummy_file_3],
        check=False,
        capture_output=True,
    )
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_valid_formatted_files_checking_with_nonexistent_one_keepgoing(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass\n")
    dummy_file_3 = write_file(tmp_path, "script3.gd", "pass\n")
    outcome = subprocess.run(
        ["gdformat", "--check", dummy_file, "nonexistent.gd", dummy_file_3],
        check=False,
        capture_output=True,
    )
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 1
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_valid_formatted_files_checking_with_invalid_one_keepgoing(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass\n")
    dummy_file_2 = write_file(tmp_path, "script2.gd", "pass x")  # invalid
    dummy_file_3 = write_file(tmp_path, "script3.gd", "pass\n")
    outcome = subprocess.run(
        ["gdformat", "--check", dummy_file, dummy_file_2, dummy_file_3],
        check=False,
        capture_output=True,
    )
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 1
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_valid_unformatted_file_diff(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass;pass")
    outcome = subprocess.run(
        ["gdformat", "--diff", dummy_file],
        check=False,
        capture_output=True,
    )
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) > 2
    assert "+++" in outcome.stderr.decode()


def test_valid_unformatted_file_indentation_using_tabs(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "func foo():\n  pass")
    outcome = subprocess.run(
        ["gdformat", "--diff", dummy_file],
        check=False,
        capture_output=True,
    )
    new_pass_lines = [
        line
        for line in outcome.stderr.decode().splitlines()
        if "pass" in line and line.startswith("+")
    ]
    assert len(new_pass_lines) == 1
    assert "\tpass" in new_pass_lines[0]


def test_valid_unformatted_file_indentation_using_spaces(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "func foo():\n  pass")
    outcome = subprocess.run(
        ["gdformat", "--diff", "--use-spaces=7", dummy_file],
        check=False,
        capture_output=True,
    )
    new_pass_lines = [
        line
        for line in outcome.stderr.decode().splitlines()
        if "pass" in line and line.startswith("+")
    ]
    assert len(new_pass_lines) == 1
    assert "       pass" in new_pass_lines[0]
