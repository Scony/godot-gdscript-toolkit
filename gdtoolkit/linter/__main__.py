"""GDScript linter

By default, nothing is being printed on success and the exitcode is 0.
On failure, python exception or list of problems is shown and exitcode is non-zero.

Usage:
  gdlint <file>... [options]
  gdlint -d

Options:
  -d --dump-default-config   Dump default config to 'gdlintrc' file
  -v --verbose               Show extra prints
  -h --help                  Show this screen.
  --version                  Show version.
"""
import sys
import os
import pkg_resources
import logging
from pathlib import Path

import yaml
from docopt import docopt

from gdtoolkit.linter import lint_code, DEFAULT_CONFIG
from gdtoolkit.linter.problem_printer import print_problem


def main():  # pylint: disable=too-many-branches
    CONFIG_FILE_NAME = "gdlintrc"

    arguments = docopt(
        __doc__,
        version="gdlint {}".format(pkg_resources.get_distribution("gdtoolkit").version),
    )

    if not isinstance(arguments, dict):
        print(arguments)  # stderr
        sys.exit(0)

    if arguments["--verbose"]:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    if arguments["--dump-default-config"]:  # TODO: error handling
        assert not os.path.isfile(CONFIG_FILE_NAME)
        with open(CONFIG_FILE_NAME, "w") as fh:
            fh.write(yaml.dump(DEFAULT_CONFIG.copy()))
        sys.exit(0)

    # TODO: add opt-based config-file providing
    # TODO: extract the algorithm
    search_dir = Path(os.getcwd())
    found_config_file_path = None
    while search_dir != Path(os.path.abspath(os.sep)):
        file_path = os.path.join(search_dir, CONFIG_FILE_NAME)
        if os.path.isfile(file_path):
            found_config_file_path = file_path
            break
        file_path = os.path.join(search_dir, ".{}".format(CONFIG_FILE_NAME))
        if os.path.isfile(file_path):
            found_config_file_path = file_path
            break
        search_dir = search_dir.parent

    if found_config_file_path is None:
        logging.info("""No 'gdlintrc' nor '.gdlintrc' found. Using default config...""")
        config = DEFAULT_CONFIG
    else:
        logging.info("Config file found: '%s'", found_config_file_path)
        with open(found_config_file_path, "r") as fh:
            config = yaml.load(fh.read(), Loader=yaml.Loader)

    logging.info("Loaded config:")
    for entry in config.items():
        logging.info(entry)

    for key in DEFAULT_CONFIG:
        if key not in config:
            logging.info(
                "Adding missing entry from defaults: %s", (key, DEFAULT_CONFIG[key])
            )
            config[key] = DEFAULT_CONFIG[key]

    problems_total = 0
    for file_path in arguments["<file>"]:
        with open(file_path, "r") as fh:  # TODO: handle exception
            content = fh.read()
            problems = lint_code(content, config)
            problems_total += len(problems)
            if len(problems) > 0:  # TODO: friendly frontend like in halint
                for problem in problems:
                    print_problem(problem, file_path)

    if problems_total > 0:
        print(
            "Failure: {} problem{} found".format(
                problems_total, "" if problems_total == 1 else "s"
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    print("Success: no problems found")


if __name__ == "__main__":
    main()
