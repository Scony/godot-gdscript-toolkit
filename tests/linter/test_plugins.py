import os
import tempfile
import textwrap

import pytest

from gdtoolkit.linter import lint_code, DEFAULT_CONFIG


def _config_with_plugin(plugin_path):
    config = DEFAULT_CONFIG.copy()
    config.update({"plugins": [plugin_path]})
    return config


PLUGIN_SOURCE = textwrap.dedent("""\
    from types import MappingProxyType
    from typing import List
    from lark import Tree, Token
    from gdtoolkit.linter.problem import Problem
    from gdtoolkit.common.utils import get_line, get_column

    def lint(parse_tree: Tree, config: MappingProxyType) -> List[Problem]:
        if "no-print-statement" in config.get("disable", []):
            return []
        problems = []
        for call_node in parse_tree.find_data("standalone_call"):
            for child in call_node.children:
                if isinstance(child, Token) and child.value == "print":
                    problems.append(Problem(
                        name="no-print-statement",
                        description="Avoid using print()",
                        line=get_line(child),
                        column=get_column(child),
                    ))
                break
        return problems
""")

CODE_WITH_PRINT = "func foo():\n\tprint('hello')\n"
CODE_WITHOUT_PRINT = "func foo():\n\tpass\n"


def test_plugin_loading_with_valid_module():
    code = "func foo():\n    pass\n"
    config = _config_with_plugin("gdtoolkit.linter.basic_checks")
    result = lint_code(code, config)
    assert isinstance(result, list)


def test_plugin_loading_with_missing_module():
    code = "func foo():\n    pass\n"
    config = _config_with_plugin("nonexistent_module_xyz")
    result = lint_code(code, config)
    assert isinstance(result, list)


def test_plugin_loading_with_empty_plugins():
    code = "func foo():\n    pass\n"
    config = DEFAULT_CONFIG.copy()
    config.update({"plugins": []})
    result = lint_code(code, config)
    assert isinstance(result, list)


def test_plugin_loading_with_no_plugins_key():
    code = "func foo():\n    pass\n"
    result = lint_code(code, DEFAULT_CONFIG)
    assert isinstance(result, list)


def test_local_plugin_detects_print(tmp_path):
    plugin_file = tmp_path / "no_print_checks.py"
    plugin_file.write_text(PLUGIN_SOURCE)

    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        config = _config_with_plugin("no_print_checks")
        result = lint_code(CODE_WITH_PRINT, config)
        print_problems = [p for p in result if p.name == "no-print-statement"]
        assert len(print_problems) == 1
        assert print_problems[0].line == 2
    finally:
        os.chdir(old_cwd)


def test_local_plugin_no_false_positive(tmp_path):
    plugin_file = tmp_path / "no_print_checks.py"
    plugin_file.write_text(PLUGIN_SOURCE)

    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        config = _config_with_plugin("no_print_checks")
        result = lint_code(CODE_WITHOUT_PRINT, config)
        print_problems = [p for p in result if p.name == "no-print-statement"]
        assert len(print_problems) == 0
    finally:
        os.chdir(old_cwd)


def test_path_based_plugin_loading(tmp_path):
    subdir = tmp_path / "ci" / "gdlint"
    subdir.mkdir(parents=True)
    plugin_file = subdir / "no_print_checks.py"
    plugin_file.write_text(PLUGIN_SOURCE)

    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        config = _config_with_plugin("ci/gdlint/no_print_checks")
        result = lint_code(CODE_WITH_PRINT, config)
        print_problems = [p for p in result if p.name == "no-print-statement"]
        assert len(print_problems) == 1
        assert print_problems[0].line == 2
    finally:
        os.chdir(old_cwd)


def test_path_based_plugin_missing_file(tmp_path):
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        config = _config_with_plugin("ci/gdlint/nonexistent")
        result = lint_code(CODE_WITH_PRINT, config)
        assert isinstance(result, list)
    finally:
        os.chdir(old_cwd)
