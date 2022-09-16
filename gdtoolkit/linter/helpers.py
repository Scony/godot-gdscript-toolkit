def is_function_public(function_name: str) -> bool:
    return not function_name.startswith("_")
