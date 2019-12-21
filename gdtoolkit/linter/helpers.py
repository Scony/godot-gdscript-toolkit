from lark import Token


def find_name_token_among_children(tree):
    for child in tree.children:
        if isinstance(child, Token) and child.type == "NAME":
            return child
    return None
