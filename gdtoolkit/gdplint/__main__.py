"""Godot Project linter

A tool for diagnosing typical Godot project problems.
On success the exitcode is 0.
On failure, python exception or list of problems is shown and exitcode is non-zero.

Usage:
  gdplint <project_path>... [options]

Options:
  -v --verbose               Show extra prints
  -h --help                  Show this screen.
  --version                  Show version.
"""
import sys
import pkg_resources
import logging
from typing import List

from docopt import docopt

from gdtoolkit.gdplint import lint_project


Path = str


def main():
    arguments = docopt(
        __doc__,
        version="gdlint {}".format(pkg_resources.get_distribution("gdtoolkit").version),
    )

    if arguments["--verbose"]:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    problems_total = 0

    project_paths: List[Path] = arguments["<project_path>"]
    for project_path in project_paths:
        problems_total += _lint_project(project_path)

    if problems_total > 0:
        print(
            "Failure: {} problem{} found".format(
                problems_total, "" if problems_total == 1 else "s"
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    print("Success: no problems found")


def _lint_project(project_path: Path) -> int:
    outcome = lint_project(project_path)
    print(outcome)
    return len(outcome)
