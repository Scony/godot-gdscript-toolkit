import subprocess

from ..common import write_file


def count_blank_lines_before(lines, pattern):
    for i, line in enumerate(lines):
        if pattern in line:
            # Looks at 3 lines above since the current maximum blank lines is 2
            start = max(0, i - 3)
            return sum(1 for line in lines[start:i] if line.strip() == "")
    return 0


def format_and_read(file_path, extra_args=None, cwd=None):
    cmd = ["gdformat", file_path]
    if extra_args:
        cmd.extend(extra_args)
    outcome = subprocess.run(cmd, cwd=cwd, check=False, capture_output=True)
    assert outcome.returncode == 0
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def run_gdformat(
    args, expected_returncode=0, expected_stdout_lines=None, expected_stderr_lines=None
):
    cmd = ["gdformat"] + args
    outcome = subprocess.run(cmd, check=False, capture_output=True)
    assert outcome.returncode == expected_returncode
    if expected_stdout_lines is not None:
        assert len(outcome.stdout.decode().splitlines()) == expected_stdout_lines
    if expected_stderr_lines is not None:
        assert len(outcome.stderr.decode().splitlines()) == expected_stderr_lines
    return outcome


def test_valid_file_formatting(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    outcome = run_gdformat(
        [dummy_file], expected_stdout_lines=2, expected_stderr_lines=0
    )
    assert outcome.returncode == 0


def test_valid_files_formatting(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    dummy_file_2 = write_file(tmp_path, "script2.gd", "pass;pass")
    run_gdformat(
        [dummy_file, dummy_file_2], expected_stdout_lines=3, expected_stderr_lines=0
    )


def test_valid_files_formatting_with_nonexistent_one_keepgoing(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    dummy_file_3 = write_file(tmp_path, "script3.gd", "pass;pass")
    outcome = run_gdformat(
        [dummy_file, "nonexistent.gd", dummy_file_3],
        expected_returncode=1,
        expected_stdout_lines=3,
    )
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_valid_files_formatting_with_invalid_one_keepgoing(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    dummy_file_2 = write_file(tmp_path, "script2.gd", "pass x")  # invalid
    dummy_file_3 = write_file(tmp_path, "script3.gd", "pass;pass")
    outcome = run_gdformat(
        [dummy_file, dummy_file_2, dummy_file_3],
        expected_returncode=1,
        expected_stdout_lines=3,
    )
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_valid_formatted_file_checking(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass\n")
    run_gdformat(
        ["--check", dummy_file], expected_stdout_lines=1, expected_stderr_lines=0
    )


def test_valid_unformatted_file_checking(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass;var x")
    run_gdformat(
        ["--check", dummy_file],
        expected_returncode=1,
        expected_stdout_lines=0,
        expected_stderr_lines=2,
    )


def test_valid_unformatted_files_checking_with_invalid_one_keepgoing(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass")
    dummy_file_2 = write_file(tmp_path, "script2.gd", "pass x")  # invalid
    dummy_file_3 = write_file(tmp_path, "script3.gd", "pass;pass")
    outcome = run_gdformat(
        ["--check", dummy_file, dummy_file_2, dummy_file_3],
        expected_returncode=1,
        expected_stdout_lines=0,
    )
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_valid_formatted_files_checking_with_nonexistent_one_keepgoing(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass\n")
    dummy_file_3 = write_file(tmp_path, "script3.gd", "pass\n")
    outcome = run_gdformat(
        ["--check", dummy_file, "nonexistent.gd", dummy_file_3],
        expected_returncode=1,
        expected_stdout_lines=1,
    )
    assert len(outcome.stderr.decode().splitlines()) > 0
    assert "Traceback" not in outcome.stderr.decode()


def test_valid_formatted_files_checking_with_invalid_one_keepgoing(tmp_path):
    dummy_file = write_file(tmp_path, "script.gd", "pass\n")
    dummy_file_2 = write_file(tmp_path, "script2.gd", "pass x")  # invalid
    dummy_file_3 = write_file(tmp_path, "script3.gd", "pass\n")
    outcome = run_gdformat(
        ["--check", dummy_file, dummy_file_2, dummy_file_3],
        expected_returncode=1,
        expected_stdout_lines=1,
    )
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


def test_not_formatting_with_default_line_length(tmp_path):
    # pylint: disable=line-too-long
    dummy_file = write_file(
        tmp_path,
        "script.gd",
        "var x = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1\n",
    )
    run_gdformat(
        ["--check", dummy_file], expected_stdout_lines=1, expected_stderr_lines=0
    )


def test_formatting_with_default_line_length(tmp_path):
    # pylint: disable=line-too-long
    dummy_file = write_file(
        tmp_path,
        "script.gd",
        "var x = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1\n",
    )
    run_gdformat(["--check", dummy_file], expected_returncode=1)


def test_formatting_with_line_length_passed_as_argument(tmp_path):
    # pylint: disable=line-too-long
    dummy_file = write_file(
        tmp_path,
        "script.gd",
        "var x = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1\n",
    )
    run_gdformat(["--check", "--line-length=80", dummy_file], expected_returncode=1)


def test_single_blank_lines_flag(tmp_path):
    test_code = (
        "class MyClass:\n"
        "    func _init():\n"
        "        pass\n"
        "\n"
        "    func method():\n"
        "        pass\n"
        "\n"
        "\n"
        "func global_func():\n"
        "    pass\n"
        "\n"
        "\n"
        "func another_global_func():\n"
        "    pass\n"
    )

    double_line_dummy_file = write_file(tmp_path, "script_double.gd", test_code)
    lines = format_and_read(double_line_dummy_file)
    assert count_blank_lines_before(lines, "func global_func():") == 2
    assert count_blank_lines_before(lines, "func method():") == 1

    single_line_dummy_file = write_file(tmp_path, "script_single.gd", test_code)
    lines2 = format_and_read(
        single_line_dummy_file, extra_args=["--single-blank-lines"]
    )
    assert count_blank_lines_before(lines2, "func global_func():") == 1
    assert count_blank_lines_before(lines2, "func method():") == 1


def test_single_blank_lines_config(tmp_path):
    write_file(tmp_path, "gdformatrc", "single_blank_lines: true\n")

    test_code = (
        "class MyClass:\n"
        "    func _init():\n"
        "        pass\n"
        "\n"
        "    func method():\n"
        "        pass\n"
        "\n"
        "\n"
        "func global_func():\n"
        "    pass\n"
    )

    dummy_file = write_file(tmp_path, "script.gd", test_code)
    lines = format_and_read(dummy_file, cwd=tmp_path)
    assert count_blank_lines_before(lines, "func global_func():") == 1
    assert count_blank_lines_before(lines, "func method():") == 1
