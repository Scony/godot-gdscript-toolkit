from types import MappingProxyType


INDENT_STRING = "\t"
INDENT_SIZE = 4
INLINE_COMMENT_OFFSET = 2

DEFAULT_SURROUNDING_EMPTY_LINES_TABLE = MappingProxyType(
    {"class_def": 1, "func_def": 1}
)
GLOBAL_SCOPE_SURROUNDING_EMPTY_LINES_TABLE = MappingProxyType(
    {"class_def": 2, "func_def": 2}
)
