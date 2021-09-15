"""GDScript formatter

Uncompromising GDScript code formatter. The only configurable thing is
max line length allowed. The rest will be taken care of by gdformat in a one,
consistent way.

Usage:
  gdformat <path>... [options]

Options:
  -c --check                 Don't write the files back,
                             just check if formatting is possible.
  -d --diff                  Don't write the files back,
                             just suggest formatting changes
                             (implies --check).
  -f --fast                  Skip safety checks.
  -l --line-length=<int>     How many characters per line to allow.
                             [default: 100]
  -h --help                  Show this screen.
  --version                  Show version.

Examples:
  echo 'tool' | gdformat -   # reads from STDIN
"""
import sys
import pkg_resources
import difflib
from typing import List, Tuple

from docopt import docopt

from gdtoolkit.formatter import format_code, check_formatting_safety
from gdtoolkit.formatter.exceptions import (
    TreeInvariantViolation,
    FormattingStabilityViolation,
    CommentPersistenceViolation,
)
from gdtoolkit.parser import parser
from gdtoolkit.common.utils import find_gd_files_from_paths
from gdtoolkit.common.exceptions import (
    lark_unexpected_token_to_str,
    lark_unexpected_input_to_str,
)

import lark


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    arguments = docopt(
        __doc__,
        version="gdformat {}".format(
            pkg_resources.get_distribution("gdtoolkit").version
        ),
    )

    if arguments["--diff"]:
        arguments["--check"] = True

    line_length = int(arguments["--line-length"])
    safety_checks = not arguments["--fast"]
    files: List[str] = find_gd_files_from_paths(
        arguments["<path>"], excluded_directories=set(".git")
    )

    if files == ["-"]:
        _format_stdin(line_length, safety_checks)
    elif arguments["--check"]:
        _check_files_formatting(files, line_length, arguments["--diff"], safety_checks)
    else:
        _format_files(files, line_length, safety_checks)


def _format_stdin(line_length: int, safety_checks: bool) -> None:
    code = sys.stdin.read()
    success, _, formatted_code = _format_code(code, line_length, "STDIN", safety_checks)
    if not success:
        sys.exit(1)
    print(formatted_code, end="")


def _check_files_formatting(
    files: List[str], line_length: int, print_diff: bool, safety_checks: bool
) -> None:
    formattable_files = set()
    failed_files = set()
    for file_path in files:
        try:
            with open(file_path, "r") as fh:
                code = fh.read()
                success, actually_formatted, formatted_code = _format_code(
                    code, line_length, file_path, safety_checks
                )
                if success and actually_formatted:
                    print("would reformat {}".format(file_path), file=sys.stderr)
                    if print_diff:
                        print(
                            "\n".join(
                                difflib.unified_diff(
                                    code.splitlines(),
                                    formatted_code.splitlines(),
                                    file_path,
                                    file_path,
                                    lineterm="",
                                )
                            ),
                            file=sys.stderr,
                        )
                    formattable_files.add(file_path)
                elif not success:
                    failed_files.add(file_path)
        except OSError as e:
            print(
                "Cannot open file '{}': {}".format(file_path, e.strerror),
                file=sys.stderr,
            )
            failed_files.add(file_path)
    if len(formattable_files) == 0:
        print(
            "{} file{} would be left unchanged".format(
                len(files), "s" if len(files) != 1 else ""
            )
        )
        sys.exit(0 if len(failed_files) == 0 else 1)
    formattable_num = len(formattable_files)
    left_unchanged_num = len(files) - formattable_num
    print(
        "{} file{} would be reformatted, {} file{} would be left unchanged.".format(
            formattable_num,
            "s" if formattable_num != 1 else "",
            left_unchanged_num,
            "s" if left_unchanged_num != 1 else "",
        ),
        file=sys.stderr,
    )
    sys.exit(1)


def _format_files(files: List[str], line_length: int, safety_checks: bool) -> None:
    formatted_files = set()
    failed_files = set()
    for file_path in files:
        try:
            with open(file_path, "r+") as fh:
                code = fh.read()
                success, actually_formatted, formatted_code = _format_code(
                    code, line_length, file_path, safety_checks
                )
                if success and actually_formatted:
                    print("reformatted {}".format(file_path))
                    formatted_files.add(file_path)
                    fh.seek(0)
                    fh.truncate(0)
                    fh.write(formatted_code)
                elif not success:
                    failed_files.add(file_path)
        except OSError as e:
            print(
                "Cannot open file '{}': {}".format(file_path, e.strerror),
                file=sys.stderr,
            )
            failed_files.add(file_path)
    reformatted_num = len(formatted_files)
    left_unchanged_num = len(files) - reformatted_num
    print(
        "{} file{} reformatted, {} file{} left unchanged.".format(
            reformatted_num,
            "s" if reformatted_num != 1 else "",
            left_unchanged_num,
            "s" if left_unchanged_num != 1 else "",
        )
    )
    sys.exit(0 if len(failed_files) == 0 else 1)


def _format_code(
    code: str, line_length: int, file_path: str, safety_checks: bool
) -> Tuple[bool, bool, str]:
    success = True
    actually_formatted = False
    formatted_code = code

    try:
        code_parse_tree = parser.parse(code, gather_metadata=True)
        comment_parse_tree = parser.parse_comments(code)
        formatted_code = format_code(
            gdscript_code=code,
            max_line_length=line_length,
            parse_tree=code_parse_tree,
            comment_parse_tree=comment_parse_tree,
        )
        if formatted_code != code:
            actually_formatted = True
            if safety_checks:
                check_formatting_safety(
                    code,
                    formatted_code,
                    max_line_length=line_length,
                    given_code_parse_tree=code_parse_tree,
                    given_code_comment_parse_tree=comment_parse_tree,
                )
    except lark.exceptions.UnexpectedToken as e:
        success = False
        print(
            f"{file_path}:\n",
            lark_unexpected_token_to_str(e, code),
            sep="\n",
            file=sys.stderr,
        )
    except lark.exceptions.UnexpectedInput as e:
        success = False
        print(
            f"{file_path}:\n",
            lark_unexpected_input_to_str(e),
            sep="\n",
            file=sys.stderr,
        )
    except TreeInvariantViolation:
        success = False
        print(
            f"{file_path}: Failed to format, formatted code parse tree differs",
            file=sys.stderr,
        )
    except FormattingStabilityViolation:
        success = False
        print(
            f"{file_path}: Failed to format, formatted code is unstable",
            file=sys.stderr,
        )
    except CommentPersistenceViolation:
        success = False
        print(
            f"{file_path}: Failed to format,",
            "some comments are missing in formatted code",
            sep="",
            file=sys.stderr,
        )
    return success, actually_formatted, formatted_code


if __name__ == "__main__":
    main()
