import os
from typing import FrozenSet, List

Path = str


def find_gd_files_from_paths(
    paths: List[Path], excluded_directories: FrozenSet[Path] = frozenset()
) -> List[Path]:
    """Finds .gd files in directories recursively and combines results to the list"""
    files = []
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path, topdown=True):
                dirnames[:] = [d for d in dirnames if d not in excluded_directories]
                files += [
                    os.path.join(dirpath, f) for f in filenames if f.endswith(".gd")
                ]
        else:
            files.append(path)
    return files
