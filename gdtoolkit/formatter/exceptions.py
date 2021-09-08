from dataclasses import dataclass


@dataclass
class TreeInvariantViolation(Exception):
    diff: str

    def __str__(self):
        return '{}(diff="{}")'.format("TreeInvariantViolation", self.diff)


@dataclass
class FormattingStabilityViolation(Exception):
    diff: str

    def __str__(self):
        return '{}(diff="{}")'.format("FormattingStabilityViolation", self.diff)


@dataclass
class CommentPersistenceViolation(Exception):
    missing_comment: str

    def __str__(self):
        return '{}(missing_comment="{}")'.format(
            "CommentPersistenceViolation", self.missing_comment
        )
