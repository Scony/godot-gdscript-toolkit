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
  --format=<format>          Output format: 'text' (default) or 'gitlab'.
  -h --help                  Show this screen.
  --version                  Show version.
"""
import sys
import os
import json
import logging
import pathlib
from typing import Dict, List, Optional
from types import MappingProxyType
from importlib.metadata import version as pkg_version

import lark
import yaml
from docopt import docopt

from gdtoolkit.linter import lint_code, DEFAULT_CONFIG
from gdtoolkit.linter.problem import Problem
from gdtoolkit.linter.problem_printer import (
    print_problem,
    generate_gitlab_codeclimate_report,
)
from gdtoolkit.common.exceptions import (
    lark_unexpected_token_to_str,
    lark_unexpected_input_to_str,
)
from gdtoolkit.common.utils import find_gd_files_from_paths


Path = str

CONFIG_FILE_NAME = "gdlintrc"
OUTPUT_FORMATS = ("text", "gitlab")


def main():
    arguments = docopt(
        __doc__,
        version="gdlint {}".format(pkg_version("gdtoolkit")),
    )

    if arguments["--verbose"]:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    if arguments["--dump-default-config"]:
        _dump_default_config()

    output_format = arguments["--format"] or "text"
    if output_format not in OUTPUT_FORMATS:
        print(
            "Unsupported format '{}'. Supported formats: {}.".format(
                output_format, ", ".join(OUTPUT_FORMATS)
            ),
            file=sys.stderr,
        )
        sys.exit(2)

    config_file_path = _find_config_file()
    config = _load_config_file_or_default(config_file_path)
    _log_config_entries(config)
    _update_config_with_missing_entries_inplace(config)

    files: List[Path] = find_gd_files_from_paths(
        arguments["<path>"], excluded_directories=set(config["excluded_directories"])
    )

    problems_per_file: Dict[str, List[Problem]] = {}
    error_count = 0
    for file_path in files:
        problems = _lint_file(file_path, config)
        if problems is None:
            error_count += 1
        else:
            problems_per_file[file_path] = problems

    _report_problems_and_exit(problems_per_file, error_count, output_format)


def _report_problems_and_exit(
    problems_per_file: Dict[str, List[Problem]],
    error_count: int,
    output_format: str,
) -> None:
    if output_format == "gitlab":
        report = generate_gitlab_codeclimate_report(problems_per_file)
        print(json.dumps(report, indent=2))
    else:
        for file_path, problems in problems_per_file.items():
            for problem in problems:
                print_problem(problem, file_path)

    problems_total = sum(len(p) for p in problems_per_file.values()) + error_count

    if problems_total > 0:
        if output_format != "gitlab":
            print(
                "Failure: {} problem{} found".format(
                    problems_total, "" if problems_total == 1 else "s"
                ),
                file=sys.stderr,
            )
        sys.exit(1)

    if output_format != "gitlab":
        print("Success: no problems found")


def _dump_default_config() -> None:
    # TODO: error handling
    assert not os.path.isfile(CONFIG_FILE_NAME)
    with open(CONFIG_FILE_NAME, "w", encoding="utf-8") as handle:
        handle.write(yaml.dump(DEFAULT_CONFIG.copy()))
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
        with open(config_file_path, "r", encoding="utf-8") as handle:
            return yaml.load(handle.read(), Loader=yaml.Loader)

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


def _lint_file(
    file_path: str, config: MappingProxyType
) -> Optional[List[Problem]]:  # TODO: friendly frontend like in halint
    # Returns the list of found problems, or 'None' when the file could not be
    # opened or parsed - in which case the reason is already reported to stderr.
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            content = handle.read()
            return lint_code(content, config)
    except OSError as exception:
        print(
            "Cannot open file '{}': {}".format(file_path, exception.strerror),
            file=sys.stderr,
        )
        return None
    except lark.exceptions.UnexpectedToken as exception:
        print(
            f"{file_path}:\n",
            lark_unexpected_token_to_str(exception, content),
            sep="\n",
            file=sys.stderr,
        )
        return None
    except lark.exceptions.UnexpectedInput as exception:
        print(
            f"{file_path}:\n",
            lark_unexpected_input_to_str(exception),
            sep="\n",
            file=sys.stderr,
        )
        return None
    except lark.indenter.DedentError as exception:
        print(
            f"{file_path}:\n",
            str(exception),
            sep="\n",
            file=sys.stderr,
        )
        return None


if __name__ == "__main__":
    main()
