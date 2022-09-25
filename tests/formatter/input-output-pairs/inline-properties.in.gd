var p1: set = __set
var p2: set = __set, get = __get
var p3: get = __get
var p4: get = __get, set = __set # TODO: add newline after to trigger stability failure
var p5 = 1: set = __set
var p6 = 1: set = __set, get = __get
var p7 = 1: get = __get
var p8 = 1: get = __get, set = __set

func __get():
	return 1

func __set(v):
	pass
