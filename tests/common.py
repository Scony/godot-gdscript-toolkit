import os


def write_file(tmp_dir, file_name, code):
    file_path = os.path.join(tmp_dir, file_name)
    with open(file_path, "w") as fh:
        fh.write(code)
        return file_path
