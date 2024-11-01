from typing import Iterator
from collections import defaultdict

from lark.indenter import Indenter
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
        if self.paren_level > 0:
            # NL handling inside parens - required for multiline lambdas
            yield from self._handle_NL_in_parens(token)
        else:
            # regular NL handling
            for produced_token in super().handle_NL(token):
                if produced_token.type == self.DEDENT_type:
                    # couple tweaks for handling multiline lambdas:
                    # 1) setting custom DEDENT metadata
                    yield Token(
                        self.DEDENT_type, None, None, token.line, None, token.line
                    )
                    # 2) producing extra NL after DEDENT to simplify grammar
                    yield token
                else:
                    yield produced_token

    def _process(self, stream):
        self.processed_tokens = []
        self.undedented_lambdas_at_paren_level = defaultdict(int)

        for produced_token in super()._process(self._record_stream(stream)):
            if (
                produced_token.type in self.CLOSE_PAREN_types
                or produced_token.type in self.LAMBDA_SEPARATOR_types
            ):
                # dedenting all undedented lambas (more than one if nested) at current paren level
                while self.undedented_lambdas_at_paren_level[self.paren_level] > 0:
                    yield from self._dedent_lambda_at_token(produced_token)
            yield produced_token

    def _record_stream(self, stream):
        for token in stream:
            self.processed_tokens.append(token)
            yield token

    # pylint: disable=invalid-name
    def _handle_NL_in_parens(self, token: Token):
        indent_str = token.rsplit("\n", 1)[1]  # tabs and spaces
        indent = indent_str.count(" ") + indent_str.count("\t") * self.tab_len

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

            # never raising DedentError here as it doesn't make sense in parens

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
