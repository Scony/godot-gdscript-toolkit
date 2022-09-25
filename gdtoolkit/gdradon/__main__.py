"""GDScript code metrics calculator

Experimental tool which converts GDScript code to Python and runs radon tool on it.

Usage:
  gdradon cc <path>... [options]

Options:
  -h --help                  Show this screen.
  --version                  Show version.

Examples:
  gdradon cc file1.gd file2.gd path/
"""
import sys
from typing import List
import pkg_resources

from docopt import docopt
from radon.complexity import cc_rank, cc_visit
from radon.visitors import Function
from radon.cli.colors import LETTERS_COLORS, RANKS_COLORS, RESET

from gdtoolkit.common.utils import find_gd_files_from_paths
from gdtoolkit.gd2py import convert_code

Path = str


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    arguments = docopt(
        __doc__,
        version="gdradon {}".format(
            pkg_resources.get_distribution("gdtoolkit").version
        ),
    )

    files: List[Path] = find_gd_files_from_paths(arguments["<path>"])
    for file_path in files:
        _cc(file_path)


def _cc(file_path: str) -> None:
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            python_code = convert_code(handle.read())
            results = cc_visit(python_code)
            if not results:
                return
            print(file_path)
            for result in results:
                letter = "F" if isinstance(result, Function) else "C"
                rank = cc_rank(result.complexity)
                # pylint: disable=duplicate-string-formatting-argument
                print(
                    "    {}{}{} {}:{} {} - {}{} ({}){}".format(
                        LETTERS_COLORS[letter],
                        letter,
                        RESET,
                        result.lineno,
                        result.col_offset,
                        result.name,
                        RANKS_COLORS[rank],
                        rank,
                        result.complexity,
                        RESET,
                    )
                )
    except OSError as exception:
        print(
            "Cannot open file '{}': {}".format(file_path, exception.strerror),
            file=sys.stderr,
        )
    except Exception as exception:  # pylint: disable=broad-except
        print(
            "Cannot process file '{}' due to exception: {}".format(
                file_path, exception
            ),
            file=sys.stderr,
        )
