from typing import Tuple, List, Optional

PreviouslyProcessedLineNumber = int
FormattedLine = Tuple[Optional[int], str]
FormattedLines = List[FormattedLine]
Outcome = Tuple[FormattedLines, PreviouslyProcessedLineNumber]
