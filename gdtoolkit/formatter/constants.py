from types import MappingProxyType


INDENT_STRING = "\t"
INDENT_SIZE = 4
INLINE_COMMENT_OFFSET = 2

DEFAULT_SURROUNDING_EMPTY_LINES_TABLE = MappingProxyType(
    {
        "class_def": 1,
        "func_def": 1,
        "static_func_def": 1,
        "remote_func_def": 1,
        "remotesync_func_def": 1,
        "master_func_def": 1,
        "mastersync_func_def": 1,
        "puppet_func_def": 1,
        "sync_func_def": 1,
    }
)
GLOBAL_SCOPE_SURROUNDING_EMPTY_LINES_TABLE = MappingProxyType(
    {
        "class_def": 2,
        "func_def": 2,
        "static_func_def": 2,
        "remote_func_def": 2,
        "remotesync_func_def": 2,
        "master_func_def": 2,
        "mastersync_func_def": 2,
        "puppet_func_def": 2,
        "sync_func_def": 2,
    }
)
