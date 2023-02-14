import os
from typing import FrozenSet, List, Optional

from lark import Tree, Token

from .types import Node

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


def find_name_token_among_children(tree: Tree) -> Optional[Token]:
    for child in tree.children:
        if isinstance(child, Token) and child.type == "NAME":
            return child
    return None


def find_tree_among_children(tree_name_to_find: str, tree: Tree) -> Optional[Tree]:
    for child in tree.children:
        if isinstance(child, Tree) and child.data == tree_name_to_find:
            return child
    return None


# TODO: remove
def get_line(node: Node) -> int:
    if isinstance(node, Tree):
        return node.meta.line
    return node.line


# TODO: remove
def get_end_line(node: Node) -> int:
    if isinstance(node, Tree):
        return node.meta.end_line
    return node.end_line


# TODO: remove
def get_column(node: Node) -> int:
    if isinstance(node, Tree):
        return node.meta.column
    return node.column
