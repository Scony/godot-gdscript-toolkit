import sys
import io
from gdtoolkit.formatter import format_code

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

formatted_code = ""
if len(sys.argv) == 3:
    formatted_code = format_code(sys.argv[1], int(sys.argv[2]))
elif len(sys.argv) == 4:
    formatted_code = format_code(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))

print(formatted_code)
