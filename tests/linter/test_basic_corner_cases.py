from gdtoolkit.linter import lint_code


def test_empty_code_linting():
    lint_code("")


def test_newlineless_code():
    code = """func foo():
    pass"""
    lint_code(code)
