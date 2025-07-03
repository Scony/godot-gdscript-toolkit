import pytest

from .common import format_and_compare


def test_ignore_shadowed_annotation_separated_from_func():
    input_code = "\n".join(['@warning_ignore("shadowed_variable")', "func f():", "\tpass"])
    expected_output_code = input_code + "\n"
    format_and_compare(input_code, expected_output_code)
