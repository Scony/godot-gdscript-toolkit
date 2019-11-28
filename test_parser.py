import os
import subprocess

import pytest

from parser import parser


def pytest_generate_tests(metafunc):
    if "gdscript_name" in metafunc.fixturenames:
        metafunc.parametrize("gdscript_name", os.listdir('scripts'))

        
def test_parsing_success(gdscript_name):
    with open(os.path.join('scripts', gdscript_name), 'r') as fh:
        code = fh.read()
        parser.parse(code)


def test_godot_check_only_success(gdscript_name):
    gdscript_path = os.path.join('scripts', gdscript_name)
    process = subprocess.Popen(['godot-server', '--check-only', '-s', gdscript_path])
    process.wait()
    assert process.returncode == 0
