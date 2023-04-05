import sys
import io
from gdtoolkit.formatter import format_code

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
formatted_code = format_code(sys.argv[1], int(sys.argv[2]))
print(formatted_code)
