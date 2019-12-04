from gdtoolkit.linter import lint_code


def test_empty_code_linting():
    lint_code('')


def test_function_name():
    code = """
func SomeName():
    pass
"""
    outcome = lint_code(code)
    assert outcome[0].name == 'function-name'
    assert outcome[0].line == 2
