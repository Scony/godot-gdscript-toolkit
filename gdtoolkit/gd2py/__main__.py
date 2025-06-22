"""GDScript-to-python converter

Experimental converter which produces syntactically correct python3 out of given
GDScript. Produced python code almost for sure will not be runnable, although its
core structure should be the same as of GDScript thus allowing usage of various
python static analysis tools like e.g. radon.

Usage:
  gd2py <path> [options]

Options:
  -h --help                  Show this screen.
  --version                  Show version.

Examples:
  gd2py file.gd              # produces python file on stdout
  gd2py ./addons/gut/gut.gd | radon cc -s -
"""
import sys
from importlib.metadata import version as pkg_version

from docopt import docopt

from . import convert_code


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    arguments = docopt(
        __doc__,
        version="gd2py {}".format(pkg_version("gdtoolkit")),
    )
    with open(arguments["<path>"], "r", encoding="utf-8") as handle:
        print(convert_code(handle.read()))
