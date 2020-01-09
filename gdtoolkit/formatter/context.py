from typing import List


class Context:  # pylint: disable=too-many-arguments
    def __init__(
        self,
        indent: int,
        previously_processed_line_number: int,
        max_line_length: int,
        gdscript_code_lines: List,
        comments: List,
    ):
        self.indent = indent
        self.previously_processed_line_number = previously_processed_line_number
        self.max_line_length = max_line_length
        self.gdscript_code_lines = gdscript_code_lines
        self.comments = comments

    def create_child_context(self, previously_processed_line_number: int):
        return Context(
            indent=self.indent + 4,
            previously_processed_line_number=previously_processed_line_number,
            max_line_length=self.max_line_length,
            gdscript_code_lines=self.gdscript_code_lines,
            comments=self.comments,
        )
