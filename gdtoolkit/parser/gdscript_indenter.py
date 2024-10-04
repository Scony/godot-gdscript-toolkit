from typing import Iterator
from collections import defaultdict

from lark.indenter import DedentError, Indenter
from lark.lexer import Token


class GDScriptIndenter(Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
    LAMBDA_SEPARATOR_types = ["COMMA"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    # TODO: guess tab length
    tab_len = 4

    def __init__(self):
        super().__init__()
        self.processed_tokens = []
        self.undedented_lambdas_at_paren_level = defaultdict(int)

    def handle_NL(self, token: Token) -> Iterator[Token]:
        indent_str = token.rsplit("\n", 1)[1]  # Tabs and spaces
        indent = indent_str.count(" ") + indent_str.count("\t") * self.tab_len

        if self.paren_level > 0:
            for new_token in self._handle_lambdas_on_newline_token_in_parens(
                token, indent, indent_str
            ):
                yield new_token
            # special handling for lambdas
            return

        yield token

        if indent > self.indent_level[-1]:
            self.indent_level.append(indent)
            yield Token.new_borrow_pos(self.INDENT_type, indent_str, token)
        else:
            while indent < self.indent_level[-1]:
                self.indent_level.pop()
                yield Token(
                    self.DEDENT_type, indent_str, None, token.line, None, token.line
                )
                # produce extra newline after dedent to simplify grammar:
                yield token

            if indent != self.indent_level[-1]:
                raise DedentError(
                    "Unexpected dedent to column %s. Expected dedent to %s"
                    % (indent, self.indent_level[-1])
                )

    def _process(self, stream):
        self.processed_tokens = []
        self.undedented_lambdas_at_paren_level = defaultdict(int)
        for token in stream:
            self.processed_tokens.append(token)
            if token.type == self.NL_type:
                yield from self.handle_NL(token)

            if token.type in self.OPEN_PAREN_types:
                self.paren_level += 1
            elif token.type in self.CLOSE_PAREN_types:
                while self.undedented_lambdas_at_paren_level[self.paren_level] > 0:
                    for new_token in self._dedent_lambda_at_token(token):
                        yield new_token
                self.paren_level -= 1
                assert self.paren_level >= 0
            elif token.type in self.LAMBDA_SEPARATOR_types:
                if self.undedented_lambdas_at_paren_level[self.paren_level] > 0:
                    for new_token in self._dedent_lambda_at_token(token):
                        yield new_token

            if token.type != self.NL_type:
                yield token

        while len(self.indent_level) > 1:
            self.indent_level.pop()
            yield Token(self.DEDENT_type, "")

        assert self.indent_level == [0], self.indent_level

    def _handle_lambdas_on_newline_token_in_parens(
        self, token: Token, indent: int, indent_str: str
    ):
        if (
            self._current_token_is_just_after_lambda_header()
            and indent > self.indent_level[-1]
        ):
            self.indent_level.append(indent)
            self.undedented_lambdas_at_paren_level[self.paren_level] += 1
            yield token
            yield Token.new_borrow_pos(self.INDENT_type, indent_str, token)
        elif (
            indent <= self.indent_level[-1]
            and self.undedented_lambdas_at_paren_level[self.paren_level] > 0
        ):
            yield token

            while indent < self.indent_level[-1]:
                self.indent_level.pop()
                self.undedented_lambdas_at_paren_level[self.paren_level] -= 1
                yield Token.new_borrow_pos(self.DEDENT_type, indent_str, token)

            if indent != self.indent_level[-1]:
                raise DedentError(
                    "Unexpected dedent to column %s. Expected dedent to %s"
                    % (indent, self.indent_level[-1])
                )

    def _dedent_lambda_at_token(self, token: Token):
        self.indent_level.pop()
        self.undedented_lambdas_at_paren_level[self.paren_level] -= 1
        yield Token.new_borrow_pos(self.NL_type, "N/A", token)
        yield Token.new_borrow_pos(self.DEDENT_type, "N/A", token)

    def _current_token_is_just_after_lambda_header(self):
        extra_rpars = [0]
        pattern_functions = [
            lambda t: t.type == "COLON",
            lambda t: t.type == "RPAR",
            lambda t: t.type == "LPAR" and extra_rpars[0] == 0,
            lambda t: t.type == "FUNC",
        ]

        def lpar_accept_function(token: Token) -> bool:
            if token.type == "RPAR":
                extra_rpars[0] += 1
            elif token.type == "LPAR":
                if extra_rpars[0] <= 0:
                    return False
                extra_rpars[0] -= 1
            return True

        accept_functions = [
            lambda t: t.type == "_NL",
            lambda t: t.type in ["_NL", "TYPE_HINT"] or t.value == "->",
            lpar_accept_function,
            lambda t: t.type in ["_NL", "NAME"],
        ]
        i = 0
        for processed_token in reversed(self.processed_tokens):
            if i >= len(pattern_functions):
                return True
            if pattern_functions[i](processed_token):
                i += 1
                continue
            if not accept_functions[i](processed_token):
                return False
        return i >= len(pattern_functions)
