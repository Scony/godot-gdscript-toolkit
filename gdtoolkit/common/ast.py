# flake8: noqa
from typing import List

from lark import Tree

from ..formatter.annotation import STANDALONE_ANNOTATIONS

from .utils import find_name_token_among_children, find_tree_among_children
from .exceptions import GDToolkitError


# pylint: disable-next=too-few-public-methods
class Annotation:
    def __init__(self, node: Tree):
        self.lark_node = node
        self.name = node.children[0].value


# pylint: disable-next=too-few-public-methods
class Statement:
    """Abstract representation of statement"""

    # TODO: remove default = [] and fix Statements w/o annotations passed
    # pylint: disable-next=dangerous-default-value
    def __init__(self, node: Tree, annotations: List[Annotation] = []):
        self.lark_node = node
        self.kind = node.data
        self.annotations = annotations
        self.sub_statements = []  # type: List[Statement]
        self.all_sub_statements = []  # type: List[Statement]

        self._load_sub_statements()

    def _load_sub_statements(self):
        if self.kind == "class_def":
            pass  # TODO: implement
        if self.kind == "property_body_def":
            raise NotImplementedError
        if self.kind in ["func_def", "static_func_def"]:
            self.sub_statements = [Statement(n) for n in self.lark_node.children[1:]]
        elif self.kind == "if_stmt":
            for branch in self.lark_node.children:
                if branch.data in ["if_branch", "elif_branch"]:
                    self.sub_statements += [Statement(n) for n in branch.children[1:]]
                else:
                    self.sub_statements += [Statement(n) for n in branch.children]
        elif self.kind == "while_stmt":
            self.sub_statements = [Statement(n) for n in self.lark_node.children[1:]]
        elif self.kind == "for_stmt":
            self.sub_statements = [Statement(n) for n in self.lark_node.children[2:]]
        elif self.kind == "match_stmt":
            for branch in self.lark_node.children:
                self.sub_statements += [Statement(n) for n in branch.children[1:]]
        for sub_statement in self.sub_statements:
            self.all_sub_statements += [
                sub_statement
            ] + sub_statement.all_sub_statements

    def __repr__(self):
        return "Statement({}:{}:{})".format(
            self.lark_node.data, self.lark_node.meta.line, self.lark_node.meta.column
        )


# pylint: disable-next=too-few-public-methods
class Parameter:
    """Abstract representation of function parameter"""

    def __init__(self, node: Tree):
        self.name = node.children[0].value


# pylint: disable-next=too-few-public-methods
class Function(Statement):
    """Abstract representation of function"""

    def __init__(self, func_def: Tree):
        super().__init__(func_def)
        self.name = ""
        self.parameters = []  # type: List[Parameter]
        self.all_statements = [self] + self.all_sub_statements  # type: ignore

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


# pylint: disable-next=too-few-public-methods
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
        self.statements = []  # type: List[Statement]

        if parse_tree.data == "start":
            start = parse_tree
            self._load_data_from_node_children(start)
        elif parse_tree.data == "class_def":
            self._load_data_from_class_def(parse_tree)
        else:
            raise GDToolkitError("Cannot load class from that node")

    def _load_data_from_node_children(self, node: Tree) -> None:
        offset = 1 if node.data == "class_def" else 0
        annotations = []
        for stmt in node.children[offset:]:
            if stmt.data == "annotation" and not _is_annotation_standalone(
                Annotation(stmt)
            ):
                annotations.append(Annotation(stmt))
                continue
            if stmt.data == "property_body_def":
                continue
            assert isinstance(stmt, Tree), stmt
            self.statements.append(Statement(stmt, annotations))
            annotations = []
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


# pylint: disable-next=too-few-public-methods
class AbstractSyntaxTree:
    """Post-processed version of parse tree - more convenient representation
    for further processing"""

    def __init__(self, parse_tree: Tree):
        self.root_class = Class(parse_tree)
        self.all_classes = [self.root_class] + self.root_class.all_sub_classes
        self.all_functions = self.root_class.all_functions


def _is_annotation_standalone(annotation: Annotation) -> bool:
    return annotation.name in STANDALONE_ANNOTATIONS
