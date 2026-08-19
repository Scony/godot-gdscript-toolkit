import json
import subprocess

from ..common import write_file


def test_valid_file_no_config(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    assert subprocess.run(["gdlint", dummy_file], check=False).returncode == 0


def test_valid_file_w_config(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
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


def test_pretty_printing_missing_file():
    outcome = subprocess.run(
        ["gdlint", "nonexistent.gd"], check=False, capture_output=True
    )
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_pretty_printing_unexpected_token(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass x")
    outcome = subprocess.run(["gdlint", dummy_file], check=False, capture_output=True)
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_linter_problem_report_in_global_scope(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "var foo = 1\nconst X = 1")
    outcome = subprocess.run(["gdlint", dummy_file], check=False, capture_output=True)
    assert outcome.returncode == 1
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert len(outcome.stderr.decode().splitlines()) >= 0
    assert "Definition out of order in global scope" in outcome.stderr.decode()


def test_gitlab_format_valid_file(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    outcome = subprocess.run(
        ["gdlint", "--format", "gitlab", dummy_file],
        check=False,
        capture_output=True,
    )
    assert outcome.returncode == 0
    assert json.loads(outcome.stdout.decode()) == []


def test_gitlab_format_invalid_file(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "var Xx = 1")
    outcome = subprocess.run(
        ["gdlint", "--format", "gitlab", dummy_file],
        check=False,
        capture_output=True,
    )
    assert outcome.returncode == 1
    report = json.loads(outcome.stdout.decode())
    assert len(report) == 1
    entry = report[0]
    assert entry["check_name"] == "class-variable-name"
    assert entry["location"]["path"] == dummy_file
    assert entry["location"]["lines"]["begin"] == 1
    assert entry["severity"] == "major"
    assert isinstance(entry["fingerprint"], str) and entry["fingerprint"]
    assert entry["description"]


def test_gitlab_format_fingerprints_are_unique(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "var Xx = 1\nvar Yy = 2")
    outcome = subprocess.run(
        ["gdlint", "--format", "gitlab", dummy_file],
        check=False,
        capture_output=True,
    )
    assert outcome.returncode == 1
    report = json.loads(outcome.stdout.decode())
    assert len(report) == 2
    fingerprints = [entry["fingerprint"] for entry in report]
    assert len(set(fingerprints)) == len(fingerprints)


def test_unsupported_format(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    outcome = subprocess.run(
        ["gdlint", "--format", "xml", dummy_file],
        check=False,
        capture_output=True,
    )
    assert outcome.returncode == 2
    assert len(outcome.stdout.decode().splitlines()) == 0
    assert "Unsupported format" in outcome.stderr.decode()
