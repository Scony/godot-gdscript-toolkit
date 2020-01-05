from dataclasses import dataclass


@dataclass
class Problem:
    name: str
    description: str
    line: int
    column: int
