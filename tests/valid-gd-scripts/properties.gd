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
	get = _get,
	set = _set
	
var p4:
	set = _set,
	get = _get
	
var p5:
	get = _get,	set = _set
	
var p6:
	set = _set, get = _get
	
#var p7:
#	set(v):
#		pass
#	get = _get

var p8:
	set = _set

var p9: set = _set
var p10: set = _set, get = _get
#var p11: get: return 1
	
func _get():
	return 1
	
func _set(v):
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
		get = _get,
		set = _set
		
	var p4:
		set = _set,
		get = _get
		
	var p5:
		get = _get,	set = _set
		
	var p6:
		set = _set, get = _get
		
	#var p7:
	#	set(v):
	#		pass
	#	get = _get

	var p8:
		set = _set

	var p9: set = _set
	var p10: set = _set, get = _get
	#var p11: get: return 1
		
	func _get():
		return 1
		
	func _set(v):
		pass
