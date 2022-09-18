import os

from gdtoolkit.formatter import format_code, check_formatting_safety


DATA_DIR = "./big-input-files"
MAX_LINE_LENGTH = 100


def pytest_generate_tests(metafunc):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    if "test_name" in metafunc.fixturenames:
        tests_in_dir = os.path.join(this_directory, DATA_DIR)
        metafunc.parametrize(
            "test_name",
            os.listdir(tests_in_dir),
        )


def test_real_world_script(test_name):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(this_dir, DATA_DIR, test_name)
    with open(input_file_path, "r", encoding="utf-8") as input_handle:
        input_code = input_handle.read()
        formatted_code = format_code(input_code, MAX_LINE_LENGTH)
        check_formatting_safety(input_code, formatted_code, MAX_LINE_LENGTH)
