import os

from .common import format_with_checks


DATA_DIR = "./big-input-files"


def pytest_generate_tests(metafunc):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    if "test_name" in metafunc.fixturenames:
        tests_in_dir = os.path.join(this_directory, DATA_DIR)
        metafunc.parametrize(
            "test_name", os.listdir(tests_in_dir),
        )


def test_real_world_script(test_name):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(this_dir, DATA_DIR, test_name)
    with open(input_file_path, "r") as input_fh:
        input_code = input_fh.read()
        format_with_checks(input_code, check_tree_invariant=True)
