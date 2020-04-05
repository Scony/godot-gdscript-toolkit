"""GDScript formatter

Uncompromising GDScript code formatter. The only configurable thing is
max line length allowed. The rest will be taken care of by gdformat in a one,
consistent way.

Usage:
  gdformat <file>... [options]

Options:
  -c --check                 Don't write the files back,
                             just check if formatting is possible.
  -l --line-length=<int>     How many characters per line to allow.
                             [default: 100]
  -h --help                  Show this screen.
  --version                  Show version.

Examples:
  echo 'tool' | gdformat -   # reads from STDIN
"""
import sys
import pkg_resources

from docopt import docopt

from gdtoolkit.formatter import format_code, check_formatting_safety
from gdtoolkit.parser import parser


# TODO: refa & tests
# pylint: disable=too-many-statements
def main():
    arguments = docopt(
        __doc__,
        version="gdformat {}".format(
            pkg_resources.get_distribution("gdtoolkit").version
        ),
    )
    files = arguments["<file>"]
    line_length = int(arguments["--line-length"])
    if files == ["-"]:
        code = sys.stdin.read()
        code_parse_tree = parser.parse(code, gather_metadata=True)
        comment_parse_tree = parser.parse_comments(code)
        formatted_code = format_code(
            gdscript_code=code,
            max_line_length=line_length,
            parse_tree=code_parse_tree,
            comment_parse_tree=comment_parse_tree,
        )
        check_formatting_safety(
            code,
            formatted_code,
            max_line_length=line_length,
            given_code_parse_tree=code_parse_tree,
            given_code_comment_parse_tree=comment_parse_tree,
        )
        print(formatted_code, end="")
    elif arguments["--check"]:
        formattable_files = set()
        for file_path in files:
            with open(file_path, "r") as fh:
                code = fh.read()
                try:
                    code_parse_tree = parser.parse(code, gather_metadata=True)
                    comment_parse_tree = parser.parse_comments(code)
                    formatted_code = format_code(
                        gdscript_code=code,
                        max_line_length=line_length,
                        parse_tree=code_parse_tree,
                        comment_parse_tree=comment_parse_tree,
                    )
                except Exception as e:
                    print(
                        "exception during formatting of {}".format(file_path),
                        file=sys.stderr,
                    )
                    raise e
                if code != formatted_code:
                    print("would reformat {}".format(file_path), file=sys.stderr)
                    try:
                        check_formatting_safety(
                            code,
                            formatted_code,
                            max_line_length=line_length,
                            given_code_parse_tree=code_parse_tree,
                            given_code_comment_parse_tree=comment_parse_tree,
                        )
                    except Exception as e:
                        print(
                            "exception during formatting of {}".format(file_path),
                            file=sys.stderr,
                        )
                        raise e
                    formattable_files.add(file_path)
        if len(formattable_files) == 0:
            print(
                "{} file{} would be left unchanged".format(
                    len(files), "s" if len(files) != 1 else "",
                )
            )
            sys.exit(0)
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
    else:
        formatted_files = set()
        for file_path in files:
            with open(file_path, "r+") as fh:
                code = fh.read()
                try:
                    code_parse_tree = parser.parse(code, gather_metadata=True)
                    comment_parse_tree = parser.parse_comments(code)
                    formatted_code = format_code(
                        gdscript_code=code,
                        max_line_length=line_length,
                        parse_tree=code_parse_tree,
                        comment_parse_tree=comment_parse_tree,
                    )
                except Exception as e:
                    print(
                        "exception during formatting of {}".format(file_path),
                        file=sys.stderr,
                    )
                    raise e
                if code != formatted_code:
                    try:
                        check_formatting_safety(
                            code,
                            formatted_code,
                            max_line_length=line_length,
                            given_code_parse_tree=code_parse_tree,
                            given_code_comment_parse_tree=comment_parse_tree,
                        )
                    except Exception as e:
                        print(
                            "exception during formatting of {}".format(file_path),
                            file=sys.stderr,
                        )
                        raise e
                    print("reformatted {}".format(file_path))
                    formatted_files.add(file_path)
                    fh.seek(0)
                    fh.truncate(0)
                    fh.write(formatted_code)
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


if __name__ == "__main__":
    main()
