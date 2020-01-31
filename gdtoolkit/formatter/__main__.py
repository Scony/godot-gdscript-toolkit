"""GDScript formatter, NOT SUITABLE FOR PRODUCTION YET!

...

Usage:
  gdformat <file>... [options]

Options:
  -c --check                 Don't write the files back,
                             just check if formatting is possible.
  -h --help                  Show this screen.
  --version                  Show version.
"""
import sys
import pkg_resources

from docopt import docopt

from gdtoolkit.formatter import format_code
from gdtoolkit.formatter import check_formatting_safety


def main():
    arguments = docopt(
        __doc__,
        version="gdformat {}".format(
            pkg_resources.get_distribution("gdtoolkit").version
        ),
    )
    files = arguments["<file>"]
    if files == ["-"]:
        code = sys.stdin.read()
        formatted_code = format_code(gdscript_code=code, max_line_length=100)
        check_formatting_safety(code, formatted_code, max_line_length=100)
        print(formatted_code, end="")
    elif arguments["--check"]:
        formattable_files = set()
        for file_path in files:
            with open(file_path, "r") as fh:
                code = fh.read()
                try:
                    formatted_code = format_code(
                        gdscript_code=code, max_line_length=100
                    )
                except Exception as e:
                    print(
                        "exception during formatting of {}".format(file_path),
                        file=sys.stderr,
                    )
                    raise e
                if code != formatted_code:
                    print("would reformat {}".format(file_path), file=sys.stderr)
                    check_formatting_safety(code, formatted_code, max_line_length=100)
                    formattable_files.add(file_path)
        if len(formattable_files) == 0:
            print(
                "{} file{} would be left unchanged".format(
                    len(files), "s" if len(files) != 1 else "",
                )
            )
            sys.exit(0)
        print(
            "{} file{} would be reformatted, {} file{} would be left unchanged.".format(
                len(formattable_files),
                "s" if len(formattable_files) != 1 else "",
                len(files),
                "s" if len(files) != 1 else "",
            ),
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        raise NotImplementedError


if __name__ == "__main__":
    main()
