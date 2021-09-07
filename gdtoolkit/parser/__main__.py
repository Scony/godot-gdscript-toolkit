"""GDScript parser

By default, nothing is being printed on success and the exitcode is 0.
On failure, python exception is shown and exitcode is non-zero.

Usage:
  gdparse <file>... [options]

Options:
  -p --pretty   Print pretty parse tree
  -v --verbose  Print parse tree
  -h --help     Show this screen.
  --version     Show version.
"""
import sys
import pkg_resources

from docopt import docopt
from gdtoolkit.parser import parser


def main():
    arguments = docopt(
        __doc__,
        version="gdparse {}".format(
            pkg_resources.get_distribution("gdtoolkit").version
        ),
    )

    if not isinstance(arguments, dict):
        print(arguments)
        sys.exit(0)

    success = True
    for file_path in arguments["<file>"]:
        success &= _parse_file(file_path, arguments)

    if not success:
        sys.exit(1)


def _parse_file(file_path, arguments):
    try:
        with open(file_path, "r") as fh:
            content = fh.read()
            tree = parser.parse(content)  # TODO: handle exception
            if arguments["--pretty"]:
                print(tree.pretty())
            elif arguments["--verbose"]:
                print(tree)
            return True
    except OSError as e:
        print(
            "Cannot open file '{}': {}".format(file_path, e.strerror),
            file=sys.stderr,
        )
    return False


if __name__ == "__main__":
    main()
