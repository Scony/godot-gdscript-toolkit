import os

from .common import format_and_compare


DATA_DIR = "./input-output-pairs"


def pytest_generate_tests(metafunc):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    if "test_name" in metafunc.fixturenames:
        tests_in_dir = os.path.join(this_directory, DATA_DIR)
        metafunc.parametrize(
            "test_name", set(f.split(".")[0] for f in os.listdir(tests_in_dir))
        )


def test_input_output_pair(test_name):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(this_dir, DATA_DIR, "{}.in.gd".format(test_name))
    output_file_path = os.path.join(this_dir, DATA_DIR, "{}.out.gd".format(test_name))
    with open(input_file_path, "r") as input_fh:
        with open(output_file_path, "r") as output_fh:
            input_code = input_fh.read()
            expected_output_code = output_fh.read()
            format_and_compare(input_code, expected_output_code)
