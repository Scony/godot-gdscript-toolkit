from typing import Any, List, Optional, Union, Iterator, Callable
from lark.tree import Meta

Node = Any  # TODO: use one from gdtoolkit and fix accordingly

Discard: Exception

class Token(str):
    type: str
    line: int
    value: Any  # TODO: remove and fix accordingly
    column: int
    end_line: int
    end_column: int
    def __init__(
        self,
        type_: str,
        value: str,
        line: int = ...,
        column: int = ...,
        end_line: int = ...,
        end_column: int = ...,
    ): ...

class Tree:
    children: List[Node]
    line: int
    value: Any  # TODO: remove and fix accordingly
    column: int
    end_line: int
    data: str
    meta: Meta
    def __init__(self, name: str, children: List[Node], meta: Optional[Meta] = ...): ...
    def iter_subtrees(self): ...
    def find_pred(
        self, pred: Callable[[Tree], bool]
    ) -> Iterator[Tree]: ...
    def find_data(self, data: str) -> Iterator[Tree]: ...
    def pretty(self, indent_str: str = ...) -> str: ...

class Lark:
    def __init__(self, grammar: Any, **options): ...
    @classmethod
    def open(
        cls: Any, grammar_filename: str, rel_to: Optional[str] = ..., **options
    ) -> Lark: ...

class UnexpectedInput: ...

class Transformer:
    def transform(self, tree: Tree) -> Tree: ...

__version__: str
