# misc
@tool
extends Node
class_name ClassName
signal signal_name
pass

# variables
var a
var b = 1
var c: int
var d: int = 1
var e := 1
var f = 1						# TODO: puppet
@export(float) var aa
@onready var aaa

# constants
const A = 1
const B: int = 1
const C := 1

# compounds
class D:
	pass


enum { AAA, BBB }
enum Named { AAA, BBB }


func foo():
	pass


static func bar():
	pass
