# a
var p1:  # inline a
	# b
	set = __set  # inline b
	# c
# d
var p2:  # inline c
	# e
	set = __set,  # inline d
	# f
	get = __get  # inline e
	# g
var p3:
	get = __get
var p4:
	get = __get,
	set = __set

var p5:
	get:
		pass
var p6:
	get:
		pass
var p7:
	set(_x):
		pass
var p8:
	set(_x):
		pass

# h
var p9:  # inline f
	# i
	set(_x):
		pass  # inline g
	# j
	get:
		return 1  # inline h
	# k
# l
var p10:  # inline i
	# m
	get:  # inline j
		# n
		var xyz = 123  # inline k
		# o
		return xyz  # inline l
		# p
	set(x):  # inline m
		# q
		var xyz = 234  # inline n
		# r
		p8 = x + 1 + xyz  # inline o
		# s
	# t
# u


func __get():
	return 1


func __set(v):
	pass
