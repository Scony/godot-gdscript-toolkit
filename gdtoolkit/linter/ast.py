from typing import List

from lark import Tree

from .helpers import find_name_token_among_children


class Function:
    """Abstract representation of function"""

    def __init__(self, func_def: Tree):
        func_header = func_def.children[0]
        name_token = find_name_token_among_children(func_header)
        self.name = name_token.value


class Class:
    """Abstract representation of class.
    Since it contains sub-classes, it forms a tree"""

    def __init__(self, parse_tree: Tree):
        self.lark_node = parse_tree
        self.name = None
        self.sub_classes = []  # type: List[Class]
        self.functions = []  # type: List[Function]

        if parse_tree.data == "start":
            start = parse_tree
            self._load_data_from_node_children(start)
        elif parse_tree.data == "class_def":
            self._load_data_from_class_def(parse_tree)
        else:
            raise Exception("Cannot load class from that node")

    def _load_data_from_node_children(self, node: Tree) -> None:
        for stmt in node.children:
            if not isinstance(stmt, Tree):
                continue
            if stmt.data == "class_def":
                self.sub_classes.append(Class(stmt))
            if stmt.data == "func_def":
                self.functions.append(Function(stmt))

    def _load_data_from_class_def(self, class_def: Tree) -> None:
        name_token = find_name_token_among_children(class_def)
        self.name = name_token.value
        self._load_data_from_node_children(class_def)


class AbstractSyntaxTree:
    """Post-processed version of parse tree - more convenient representation
    for further processing"""

    def __init__(self, parse_tree: Tree):
        self.root_class = Class(parse_tree)
        self.classes = self._gather_all_classes_from_class_tree(self.root_class)

    def _gather_all_classes_from_class_tree(self, a_class: Class) -> List[Class]:
        classes = [a_class]
        for sub_class in a_class.sub_classes:
            classes += self._gather_all_classes_from_class_tree(sub_class)
        return classes
