# a
# b
@tool # inline a
# c

var a

# d
@onready # inline b
# e
var b # inline c
# f

@onready
# g
@export_range(1, 100, 1, "or_greater") # inline d
# h
var c: int = 50
# i

class Foo:
	# j
	@onready var d # inline e
	# k
	@onready # inline f
	# l
	var e
	
