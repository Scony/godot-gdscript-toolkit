"""GDScript formatter, NOT SUITABLE FOR PRODUCTION YET!

...

Usage:
  gdformat <file>... [options]

Options:
  -h --help                  Show this screen.
  --version                  Show version.
"""
import sys
import pkg_resources

from docopt import docopt

from gdtoolkit.formatter import format_code


def main():
    arguments = docopt(
        __doc__,
        version="gdformat {}".format(
            pkg_resources.get_distribution("gdtoolkit").version
        ),
    )
    if arguments["<file>"] == ["-"]:
        code = sys.stdin.read()
        print(format_code(gdscript_code=code, max_line_length=100), end="")
    else:
        raise NotImplementedError


if __name__ == "__main__":
    main()
