from gdtoolkit.gdplint import lint_project

from ..common import write_file

def test_valid_preload_path(tmp_path):
    write_file(tmp_path, "script_a.gd", "")
    write_file(tmp_path, "script_b.gd", "const A = preload(\"script_a.gd\")")
    assert lint_project(tmp_path) == []

def test_invalid_preload_path(tmp_path):
    write_file(tmp_path, "script_b.gd", "const A = preload(\"script_a.gd\")")
    # assert lint_project(tmp_path) != []
    # TODO: check error precisely
