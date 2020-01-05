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

    for file_path in arguments["<file>"]:
        with open(file_path, "r") as fh:  # TODO: handle exception
            content = fh.read()
            tree = parser.parse(content)  # TODO: handle exception
            if arguments["--pretty"]:
                print(tree.pretty())
            elif arguments["--verbose"]:
                print(tree)


if __name__ == "__main__":
    main()
