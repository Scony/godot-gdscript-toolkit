import os


def write_file(tmp_dir, file_name, code):
    file_path = os.path.join(tmp_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as handle:
        handle.write(code)
        return file_path
