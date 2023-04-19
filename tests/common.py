import os


GODOT_SERVER = "godot4-latest"


def write_file(a_dir, file_name, code):
    file_path = os.path.join(a_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as handle:
        handle.write(code)
        return file_path


def write_project_settings(a_dir):
    write_file(
        a_dir,
        "project.godot",
        """[debug]
    gdscript/warnings/inference_on_variant=1
    gdscript/warnings/native_method_override=1
    gdscript/warnings/get_node_default_without_onready=1
    gdscript/warnings/onready_with_export=1
    """,
    )
