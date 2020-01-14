from typing import Union, Tuple, List, Optional
from dataclasses import dataclass

from lark import Tree, Token


Node = Union[Tree, Token]
PreviouslyProcessedLineNumber = int
FormattedLines = List[Tuple[Optional[int], str]]
Outcome = Tuple[FormattedLines, PreviouslyProcessedLineNumber]


@dataclass
class Prefix:
    string: str
    line: int
