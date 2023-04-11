class SubClass:
	enum NamedEnum { A, B, C }


var a: Array[int]
var b: Array[int] = [1]
const C: Array[int] = [1]
var e: Array[SubClass.NamedEnum]


func foo(d: Array[int]) -> Array[int]:
	return [1]
