"""Regression coverage for standalone GDScript warning annotations.

See https://github.com/Scony/godot-gdscript-toolkit/issues/394
"""
import pytest

from gdtoolkit.formatter import format_code


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
