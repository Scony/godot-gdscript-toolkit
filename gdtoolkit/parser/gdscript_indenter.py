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
        # TODO: handle newlines etc. in between tokens
        return (
            len(self.processed_tokens) > 0
            and self.processed_tokens[-2].type == "COLON"
            and self.processed_tokens[-3].type == "RPAR"
            and self.processed_tokens[-4].type == "LPAR"
            and (
                self.processed_tokens[-5].type == "FUNC"
                or (
                    self.processed_tokens[-5].type == "NAME"
                    and self.processed_tokens[-6].type == "FUNC"
                )
            )
        ) or (
            len(self.processed_tokens) > 0
            and self.processed_tokens[-2].type == "COLON"
            and self.processed_tokens[-3].type == "TYPE_HINT"
            and self.processed_tokens[-4].value == "->"
            and self.processed_tokens[-5].type == "RPAR"
            and self.processed_tokens[-6].type == "LPAR"
            and (
                self.processed_tokens[-7].type == "FUNC"
                or (
                    self.processed_tokens[-7].type == "NAME"
                    and self.processed_tokens[-8].type == "FUNC"
                )
            )
        )
