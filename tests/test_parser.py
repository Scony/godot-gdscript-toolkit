import os
import subprocess
import shutil

import pytest

from gdtoolkit.parser import parser


DATA_DIR = 'valid-gd-scripts'
GODOT_SERVER = 'godot-server'


def pytest_generate_tests(metafunc):
    if 'gdscript_path' in metafunc.fixturenames:
        metafunc.parametrize(
            'gdscript_path',
            [os.path.join(DATA_DIR, x) for x in os.listdir(DATA_DIR)]
        )

        
def test_parsing_success(gdscript_path):
    with open(gdscript_path, 'r') as fh:
        code = fh.read()
        parser.parse(code)      # just checking if not throwing


@pytest.mark.skipif(shutil.which(GODOT_SERVER) is None, reason="requires godot server")
def test_godot_check_only_success(gdscript_path):
    process = subprocess.Popen([GODOT_SERVER, '--check-only', '-s', gdscript_path])
    process.wait()
    assert process.returncode == 0
