import re
from functools import partial

from .. import Problem


def lint(gdscript_code, config):
    disable = config["disable"]
    checks_to_run_w_code = [
        (
            "max-line-length",
            partial(_max_line_length_check, config["max-line-length"]),
        ),
        ("max-file-lines", partial(_max_file_lines_check, config["max-file-lines"]),),
        ("trailing-whitespace", _trailing_ws_check,),
        ("mixed-tabs-and-spaces", _mixed_tabs_and_spaces_check,),
    ]
    problem_clusters = map(
        lambda x: x[1](gdscript_code) if x[0] not in disable else [],
        checks_to_run_w_code,
    )
    problems = [problem for cluster in problem_clusters for problem in cluster]
    return problems


def _max_line_length_check(threshold, code):
    problems = []
    lines = code.splitlines()
    for line_number in range(len(lines)):
        if len(lines[line_number]) > threshold:
            problems.append(
                Problem(
                    name="max-line-length",
                    description="Max allowed line length ({}) exceeded".format(
                        threshold
                    ),
                    line=line_number + 1,
                    column=0,
                )
            )
    return problems


def _max_file_lines_check(threshold, code):
    problems = []
    lines = code.splitlines()
    if len(lines) > threshold:
        problems.append(
            Problem(
                name="max-file-lines",
                description="Max allowed file lines num ({}) exceeded".format(
                    threshold
                ),
                line=len(lines),
                column=0,
            )
        )
    return problems


def _trailing_ws_check(code):
    problems = []
    lines = code.splitlines()
    for line_number in range(len(lines)):
        line = lines[line_number]
        if re.search("\s$", line) is not None:
            problems.append(
                Problem(
                    name="trailing-whitespace",
                    description="Trailing whitespace(s)",
                    line=line_number + 1,
                    column=0,
                )
            )
    return problems


def _mixed_tabs_and_spaces_check(code):
    problems = []
    lines = code.splitlines()
    for line_number in range(len(lines)):
        line = lines[line_number]
        if re.search("^(\t+ +| +\t+)", line) is not None:
            problems.append(
                Problem(
                    name="mixed-tabs-and-spaces",
                    description="Mixed tabs and spaces",
                    line=line_number + 1,
                    column=0,
                )
            )
    return problems
