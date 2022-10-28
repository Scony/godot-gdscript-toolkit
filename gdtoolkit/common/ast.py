from typing import List

from lark import Tree

from .utils import find_name_token_among_children, find_tree_among_children


# pylint: disable=too-few-public-methods
class Parameter:
    """Abstract representation of function parameter"""

    def __init__(self, node: Tree):
        self.name = node.children[0].value


# pylint: disable=too-few-public-methods
class Function:
    """Abstract representation of function"""

    def __init__(self, func_def: Tree):
        self.lark_node = func_def
        self.name = ""
        self.parameters = []  # type: List[Parameter]

        self._load_data_from_func_def(func_def)

    def _load_data_from_func_def(self, func_def: Tree) -> None:
        func_header = func_def.children[0]
        name_token = find_name_token_among_children(func_header)
        self.name = name_token.value  # type: ignore
        func_args = find_tree_among_children("func_args", func_header)
        self.parameters = [
            Parameter(c)
            for c in func_args.children  # type: ignore
            if c.data != "trailing_comma"
        ]


# pylint: disable=too-few-public-methods
class Class:
    """Abstract representation of class.
    Since it contains sub-classes, it forms a tree"""

    def __init__(self, parse_tree: Tree):
        self.lark_node = parse_tree
        self.name = None
        self.sub_classes = []  # type: List[Class]
        self.all_sub_classes = []  # type: List[Class]
        self.functions = []  # type: List[Function]
        self.all_functions = []  # type: List[Function]

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
                sub_class = Class(stmt)
                self.sub_classes.append(sub_class)
                self.all_sub_classes += [sub_class] + sub_class.all_sub_classes
                self.all_functions += sub_class.all_functions
            if stmt.data == "func_def":
                function = Function(stmt)
                self.functions.append(function)
                self.all_functions.append(function)

    def _load_data_from_class_def(self, class_def: Tree) -> None:
        name_token = find_name_token_among_children(class_def)
        self.name = name_token.value  # type: ignore
        self._load_data_from_node_children(class_def)


# pylint: disable=too-few-public-methods
class AbstractSyntaxTree:
    """Post-processed version of parse tree - more convenient representation
    for further processing"""

    def __init__(self, parse_tree: Tree):
        self.root_class = Class(parse_tree)
        self.all_classes = [self.root_class] + self.root_class.all_sub_classes
        self.all_functions = self.root_class.all_functions
