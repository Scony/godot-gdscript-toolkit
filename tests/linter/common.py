from gdtoolkit.linter import lint_code, DEFAULT_CONFIG
from gdtoolkit.common.utils import get_line


def simple_ok_check(code, **kwargs):
    extra_disable = [] if "disable" not in kwargs else kwargs["disable"]
    config = DEFAULT_CONFIG.copy()
    config.update({"disable": extra_disable})
    outcome = lint_code(code, config)
    assert len(outcome) == 0, outcome


def simple_nok_check(code, check_name, line=2, **kwargs):
    extra_disable = [] if "disable" not in kwargs else kwargs["disable"]
    config_w_disable = DEFAULT_CONFIG.copy()
    config_w_disable.update({"disable": [check_name] + extra_disable})
    assert len(lint_code(code, config_w_disable)) == 0

    config = DEFAULT_CONFIG.copy()
    config.update({"disable": extra_disable})
    outcome = lint_code(code, config)
    assert len(outcome) == 1
    assert outcome[0].name == check_name
    assert get_line(outcome[0]) == line
