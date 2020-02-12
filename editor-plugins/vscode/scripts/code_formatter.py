import sys
from gdtoolkit.formatter import format_code

formatted_code = format_code(sys.argv[1], int(sys.argv[2]))
print(formatted_code)