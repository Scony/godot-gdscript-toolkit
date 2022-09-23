# a
# b
@tool  # inline a
# c

var a  # inline b

# d

# e
@onready var b  # inline c  # inline d
# f

# g

# h
@onready @export_range(1, 100, 1, "or_greater") var c: int = 50
# i


class Foo:
	# j
	@onready var d  # inline e  # inline f
	# k

	# l
	@onready var e
