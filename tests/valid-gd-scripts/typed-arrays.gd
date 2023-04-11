extends Node

class SubClass:
	enum NamedEnum { A, B, C }


func _ready():
	var r: Array[int] = [1,2,3]
	print([1,2.1] as Array[int])
	var r2: Array[SubClass.NamedEnum]
	#print([1,2] is Array[int])
	#print([1,2.0] is Array[int])
	#var rr: Array[Array[int]] = [[1]]
	#var d: Dictionary[int,int] = {1:1}

