var p1:
	set = __set
var p2:
	set = __set,
	get = __get

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


func __get():
	return 1


func __set(v):
	pass
