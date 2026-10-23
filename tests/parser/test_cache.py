import os
from importlib.metadata import version
from unittest.mock import patch

import pytest

from gdtoolkit.parser.parser import Parser


@pytest.mark.parametrize(
    "method,kwargs,cache_name",
    [
        ("parse", {}, "parser"),
        ("parse", {"gather_metadata": True}, "parser_with_metadata"),
        ("parse_comments", {}, "parser_comments"),
    ],
)
def test_cache_directory_created_concurrently(tmp_path, method, kwargs, cache_name):
    cache_root = tmp_path / "gdtoolkit"
    cache_root.mkdir()
    cache_directory = cache_root / version("gdtoolkit")
    original_makedirs = os.makedirs

    def makedirs_after_other_process(path, *args, **options):
        # Another process creates the directory after our existence check,
        # but before our mkdir call reaches the filesystem.
        if path == str(cache_directory):
            original_makedirs(path)
        return original_makedirs(path, *args, **options)

    with patch(
        "gdtoolkit.parser.parser.get_cache_directory", return_value=str(tmp_path)
    ):
        fresh_parser = Parser()
    with patch("gdtoolkit.parser.parser.os.makedirs", makedirs_after_other_process):
        tree = getattr(fresh_parser, method)("extends Node\n", **kwargs)

    assert tree.data == "start"
    assert (cache_directory / (cache_name + ".pickle")).is_file()


def test_cache_directory_path_is_a_file(tmp_path):
    cache_root = tmp_path / "gdtoolkit"
    cache_root.mkdir()
    cache_directory = cache_root / version("gdtoolkit")
    cache_directory.write_text("not a directory", encoding="utf-8")

    with patch(
        "gdtoolkit.parser.parser.get_cache_directory", return_value=str(tmp_path)
    ):
        fresh_parser = Parser()

    with pytest.raises(OSError):
        fresh_parser.parse("extends Node\n")

    assert cache_directory.read_text(encoding="utf-8") == "not a directory"
