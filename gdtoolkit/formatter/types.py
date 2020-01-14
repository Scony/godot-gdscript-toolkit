from typing import Union
from dataclasses import dataclass

from lark import Tree, Token


Node = Union[Tree, Token]


@dataclass
class Prefix:
    string: str
    line: int
