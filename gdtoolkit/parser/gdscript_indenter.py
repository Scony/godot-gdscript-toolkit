from typing import Iterator

from lark import Token, indenter


class GDScriptIndenter(indenter.Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    # TODO: guess tab length
    tab_len = 4

    def handle_NL(self, token: Token) -> Iterator[Token]:
        if self.paren_level > 0:
            return              # TODO: special handling for lambdas

        yield token

        indent_str = token.rsplit("\n", 1)[1]  # Tabs and spaces
        indent = indent_str.count(" ") + indent_str.count("\t") * self.tab_len

        if indent > self.indent_level[-1]:
            self.indent_level.append(indent)
            yield Token.new_borrow_pos(self.INDENT_type, indent_str, token)
        else:
            while indent < self.indent_level[-1]:
                self.indent_level.pop()
                yield Token.new_borrow_pos(self.DEDENT_type, indent_str, token)
                # produce extra newline after dedent to simplify grammar:
                yield token

            if indent != self.indent_level[-1]:
                raise DedentError(
                    "Unexpected dedent to column %s. Expected dedent to %s"
                    % (indent, self.indent_level[-1])
                )

    def _process(self, stream):
        for token in stream:
            if token.type == self.NL_type:
                yield from self.handle_NL(token)
            else:
                yield token

            if token.type in self.OPEN_PAREN_types:
                self.paren_level += 1
            elif token.type in self.CLOSE_PAREN_types:
                self.paren_level -= 1
                assert self.paren_level >= 0

        while len(self.indent_level) > 1:
            self.indent_level.pop()
            yield Token(self.DEDENT_type, "")

        assert self.indent_level == [0], self.indent_level

    # def process(self, stream):
    #     import pdb;pdb.set_trace()
    #     self.paren_level = 0
    #     self.indent_level = [0]
    #     return self._process(stream)
