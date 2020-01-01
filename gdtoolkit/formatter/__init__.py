from ..parser import parser


def format_code(gdscript_code: str, max_line_length: int) -> str:
    assert max_line_length > 0
    parse_tree = parser.parse(gdscript_code, gather_metadata=True)
    formatted_lines = []
    previously_added_line_number = 0
    for statement in parse_tree.children:
        blank_lines = _blank_lines_between(previously_added_line_number, statement.line)
        if blank_lines > 0 and previously_added_line_number != 0:
            formatted_lines += [""] * blank_lines
        previously_added_line_number = statement.line
        if statement.data == "tool_stmt":
            formatted_lines.append("tool")
    formatted_lines.append("")
    return "\n".join(formatted_lines)


def _blank_lines_between(previously_added_line_number: int, statement_line: int) -> int:
    return statement_line - previously_added_line_number - 1
