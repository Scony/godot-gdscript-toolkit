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
	get: pass
var p6:
	get:
		pass
var p7:
	set(_x): pass
var p8:
	set(_x):
		pass

var p9:
	set(_x): pass
	get: return 1
var p9x:
	get(): return 1
var p10:
	get:
		var xyz = 123
		return xyz
	set(x):
		var xyz = 234
		p8 = x + 1 + xyz

func __get():
	return 1

func __set(v):
	pass
