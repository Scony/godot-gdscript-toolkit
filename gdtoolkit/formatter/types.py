from typing import Union, Tuple, List, Optional

from lark import Tree, Token


Node = Union[Tree, Token]
PreviouslyProcessedLineNumber = int
FormattedLine = Tuple[Optional[int], str]
FormattedLines = List[FormattedLine]
Outcome = Tuple[FormattedLines, PreviouslyProcessedLineNumber]
