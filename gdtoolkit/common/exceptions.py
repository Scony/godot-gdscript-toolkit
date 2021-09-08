import lark


# TODO: use in formatter/linter


def lark_unexpected_input_to_str(exception: lark.exceptions.UnexpectedInput):
    return str(exception).strip()


def lark_unexpected_token_to_str(exception: lark.exceptions.UnexpectedToken, code: str):
    return f"{exception.get_context(code)}\n{exception}".strip()
