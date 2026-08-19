import sys
import hashlib
from typing import Dict, List

from .problem import Problem


def print_problem(problem: Problem, file_path: str) -> None:  # TODO: colors
    print(
        "{}:{}: Error: {} ({})".format(
            file_path,
            problem.line,
            problem.description,
            problem.name,
        ),
        file=sys.stderr,
    )


def generate_gitlab_codeclimate_report(
    problems_per_file: Dict[str, List[Problem]]
) -> List[dict]:
    """Build a GitLab Code Quality report from linter problems.

    The structure follows the subset of the Code Climate spec that GitLab
    consumes - see
    https://docs.gitlab.com/ee/ci/testing/code_quality.html#implement-a-custom-tool
    """
    report = []
    for file_path, problems in problems_per_file.items():
        for problem in problems:
            fingerprint = hashlib.md5(
                "{}:{}:{}:{}:{}".format(
                    file_path,
                    problem.line,
                    problem.column,
                    problem.name,
                    problem.description,
                ).encode("utf-8")
            ).hexdigest()
            report.append(
                {
                    "description": problem.description,
                    "check_name": problem.name,
                    "fingerprint": fingerprint,
                    "severity": "major",
                    "location": {
                        "path": file_path,
                        "lines": {"begin": problem.line},
                    },
                }
            )
    return report
