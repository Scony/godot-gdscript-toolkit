from dataclasses import dataclass

from ..common.exceptions import GDToolkitError


@dataclass
class TreeInvariantViolation(GDToolkitError):
    diff: str

    def __str__(self):
        return '{}(diff="{}")'.format("TreeInvariantViolation", self.diff)


@dataclass
class FormattingStabilityViolation(GDToolkitError):
    diff: str

    def __str__(self):
        return '{}(diff="{}")'.format("FormattingStabilityViolation", self.diff)


@dataclass
class CommentPersistenceViolation(GDToolkitError):
    missing_comment: str

    def __str__(self):
        return '{}(missing_comment="{}")'.format(
            "CommentPersistenceViolation", self.missing_comment
        )
