from lark import Token


def find_name_token_among_children(tree):
    for child in tree.children:
        if isinstance(child, Token) and child.type == "NAME":
            return child
    return None


def is_function_public(function_name: str) -> bool:
    return not function_name.startswith("_")
