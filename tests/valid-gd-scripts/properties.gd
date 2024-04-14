extends Node

var p1:
	set(value):
		pass
	get:
		pass

var p2 : int = 1:
	get: pass;pass;return 1
	set(value): pass;pass
	
var p3:
	get = __get,
	set = __set
	
var p4:
	set = __set,
	get = __get
	
var p5:
	get = __get,	set = __set
	
var p6:
	set = __set, get = __get
	
#var p7:
#	set(v):
#		pass
#	get = __get

var p8:
	set = __set

var p9: set = __set
var p10: set = __set, get = __get
#var p11: get: return 1
	
func __get():
	return 1
	
func __set(v):
	pass
	
class Foo:
	var p1:
		set(value):
			pass
		get:
			pass

	var p2 = 1:
		get: pass;pass
		set(value): pass;pass
		
	var p3:
		get = __get,
		set = __set
		
	var p4:
		set = __set,
		get = __get
		
	var p5:
		get = __get,	set = __set
		
	var p6:
		set = __set, get = __get
		
	#var p7:
	#	set(v):
	#		pass
	#	get = __get

	var p8:
		set = __set

	var p9: set = __set
	var p10: set = __set, get = __get
	#var p11: get: return 1
		
	func __get():
		return 1
		
	func __set(v):
		pass

var p11:
	set(value):
		pass
	get():
		pass
