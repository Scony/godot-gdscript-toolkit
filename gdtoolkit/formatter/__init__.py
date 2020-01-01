from ..parser import parser


def format_code(gdscript_code: str, max_line_length: int) -> str:
    assert max_line_length > 0
    parse_tree = parser.parse(gdscript_code, gather_metadata=True)
    formatted_lines = []
    for x in parse_tree.children:
        if x.data == "tool_stmt":
            formatted_lines.append("tool")
    formatted_lines.append("")
    return "\n".join(formatted_lines)
