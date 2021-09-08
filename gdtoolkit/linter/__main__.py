"""GDScript linter

A tool for diagnosing typical GDScript code problems.
On success and the exitcode is 0.
On failure, python exception or list of problems is shown and exitcode is non-zero.

Usage:
  gdlint <path>... [options]
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
import pathlib
from typing import List, Optional
from types import MappingProxyType

import lark
import yaml
from docopt import docopt

from gdtoolkit.linter import lint_code, DEFAULT_CONFIG
from gdtoolkit.linter.problem_printer import print_problem
from gdtoolkit.common.exceptions import (
    lark_unexpected_token_to_str,
    lark_unexpected_input_to_str,
)
from gdtoolkit.common.utils import find_gd_files_from_paths


Path = str

CONFIG_FILE_NAME = "gdlintrc"


def main():
    arguments = docopt(
        __doc__,
        version="gdlint {}".format(pkg_resources.get_distribution("gdtoolkit").version),
    )

    if arguments["--verbose"]:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    if arguments["--dump-default-config"]:
        _dump_default_config()

    config_file_path = _find_config_file()
    config = _load_config_file_or_default(config_file_path)
    _log_config_entries(config)
    _update_config_with_missing_entries_inplace(config)

    problems_total = 0

    files: List[Path] = find_gd_files_from_paths(
        arguments["<path>"], excluded_directories=set(config["excluded_directories"])
    )
    for file_path in files:
        problems_total += _lint_file(file_path, config)

    if problems_total > 0:
        print(
            "Failure: {} problem{} found".format(
                problems_total, "" if problems_total == 1 else "s"
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    print("Success: no problems found")


def _dump_default_config() -> None:
    # TODO: error handling
    assert not os.path.isfile(CONFIG_FILE_NAME)
    with open(CONFIG_FILE_NAME, "w") as fh:
        fh.write(yaml.dump(DEFAULT_CONFIG.copy()))
    sys.exit(0)


def _find_config_file() -> Optional[str]:
    search_dir = pathlib.Path(os.getcwd())
    config_file_path = None
    while search_dir != pathlib.Path(os.path.abspath(os.sep)):
        file_path = os.path.join(search_dir, CONFIG_FILE_NAME)
        if os.path.isfile(file_path):
            config_file_path = file_path
            break
        file_path = os.path.join(search_dir, ".{}".format(CONFIG_FILE_NAME))
        if os.path.isfile(file_path):
            config_file_path = file_path
            break
        search_dir = search_dir.parent
    return config_file_path


def _load_config_file_or_default(config_file_path: Optional[str]) -> MappingProxyType:
    # TODO: error handling
    if config_file_path is not None:
        logging.info("Config file found: '%s'", config_file_path)
        with open(config_file_path, "r") as fh:
            return yaml.load(fh.read(), Loader=yaml.Loader)

    logging.info("""No 'gdlintrc' nor '.gdlintrc' found. Using default config...""")
    return DEFAULT_CONFIG


def _log_config_entries(config: MappingProxyType) -> None:
    logging.info("Loaded config:")
    for entry in config.items():
        logging.info(entry)


def _update_config_with_missing_entries_inplace(config: dict) -> None:
    for key in DEFAULT_CONFIG:
        if key not in config:
            logging.info(
                "Adding missing entry from defaults: %s", (key, DEFAULT_CONFIG[key])
            )
            config[key] = DEFAULT_CONFIG[key]


def _lint_file(file_path: str, config: MappingProxyType) -> int:
    try:
        with open(file_path, "r") as fh:
            content = fh.read()
            problems = lint_code(content, config)
            if len(problems) > 0:  # TODO: friendly frontend like in halint
                for problem in problems:
                    print_problem(problem, file_path)
            return len(problems)
    except OSError as e:
        print(
            "Cannot open file '{}': {}".format(file_path, e.strerror),
            file=sys.stderr,
        )
        return 1
    except lark.exceptions.UnexpectedToken as e:
        print(
            f"{file_path}:\n",
            lark_unexpected_token_to_str(e, content),
            sep="\n",
            file=sys.stderr,
        )
        return 1
    except lark.exceptions.UnexpectedInput as e:
        print(
            f"{file_path}:\n",
            lark_unexpected_input_to_str(e),
            sep="\n",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    main()
