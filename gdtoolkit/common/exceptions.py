import lark


# TODO: use in formatter/linter
def lark_unexpected_input_to_str(exception: lark.exceptions.UnexpectedInput, code):
    return f"{exception.get_context(code)}{exception}".strip()
