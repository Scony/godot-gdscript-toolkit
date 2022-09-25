import os

DATA_DIR = "./input-output-pairs"


def pytest_generate_tests(metafunc):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    if "python_file" in metafunc.fixturenames:
        data_dir = os.path.join(this_directory, DATA_DIR)
        metafunc.parametrize(
            "python_file", set(f for f in os.listdir(data_dir) if f.endswith(".py"))
        )


def test_compilation(python_file):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    python_file_path = os.path.join(this_dir, DATA_DIR, python_file)
    with open(python_file_path, "r", encoding="utf-8") as handle:
        compile(handle.read(), filename="<string>", mode="exec")
