"""Regression coverage for standalone GDScript warning annotations.

See https://github.com/Scony/godot-gdscript-toolkit/issues/394
"""
import pytest

from gdtoolkit.formatter import format_code, check_formatting_safety


@pytest.mark.parametrize(
    "source,annotation,following_declaration",
    [
        (
            '@warning_ignore_start("UNUSED_SIGNAL")\nsignal say(message: String)\n',
            '@warning_ignore_start("UNUSED_SIGNAL")',
            "signal say(message: String)",
        ),
        (
            '@warning_ignore_start("integer_division")\nconst TIMEOUT := 1000 / 5\n',
            '@warning_ignore_start("integer_division")',
            "const TIMEOUT",
        ),
        (
            '@warning_ignore_restore("integer_division")\nvar time_left := 1\n',
            '@warning_ignore_restore("integer_division")',
            "var time_left",
        ),
    ],
)
def test_standalone_warning_annotations_keep_their_own_lines(
    source, annotation, following_declaration
):
    result = format_code(source, max_line_length=100)
    assert annotation in result
    assert following_declaration in result
    assert annotation + "\n" in result, result
    assert annotation + " " + following_declaration not in result

@pytest.mark.parametrize(
    "source,annotation",
    [
        (
            '@warning_ignore("shadowed_global_identifier")\n@export var floor := 1\n',
            '@warning_ignore("shadowed_global_identifier")',
        ),
        (
            '@warning_ignore("integer_division")\nconst VELOCITY_TIMEOUT := 1000 / 5\n',
            '@warning_ignore("integer_division")',
        ),
        (
            '@warning_ignore("integer_division")\nvar count := 1000 / 5\n',
            '@warning_ignore("integer_division")',
        ),
    ],
)
def test_warning_ignore_on_declarations_remains_separate(source, annotation):
    result = format_code(source, max_line_length=100)
    assert result.startswith(annotation + "\n"), result
    assert format_code(result, max_line_length=100) == result
    check_formatting_safety(source, result, 100)
