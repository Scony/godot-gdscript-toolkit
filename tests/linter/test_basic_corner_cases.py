from gdtoolkit.linter import lint_code


def test_empty_code_linting():
    lint_code("")


def test_newlineless_code():
    code = """func foo():
    pass"""
    lint_code(code)


def test_docstring():
    code = '"""\nhello world!\n"""'
    lint_code(code)


def test_trailing_comma_in_params_list():
    code = """static func _is_agent_placement_position_valid(
    position,
    radius,
    existing_units,
    navigation_map_rid,):pass"""
    lint_code(code)
