from typing import Tuple, List, Optional, Any


# Node = Union[Tree, Token]  # TODO: uncomment and fix accordingly
Node = Any
PreviouslyProcessedLineNumber = int
FormattedLines = List[Tuple[Optional[int], str]]
Outcome = Tuple[FormattedLines, PreviouslyProcessedLineNumber]
