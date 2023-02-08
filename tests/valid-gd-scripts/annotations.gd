@tool
extends Node

var x

@onready

@export_range(1, 100, 1, "or_greater")
var ranged_var: int = 50

@onready @export_range(1, 100, 1, "or_greater") var ranged_var_2: int = 50

# @onready func foo():
# 	pass
# @onready
# func bar():
# 	pass
# @onready const X = 1
# @master var x

@onready @export_range(1, 100, 1, "or_greater")
var ranged_var_3: int = 50

pass;pass
@onready var y;pass
@onready @export_range(1, 100, 1, "or_greater") var ranged_var_4: int = 50;pass
@onready @export_range(1, 100, 1, "or_greater") var ranged_var_5: int = 50;@onready @export_range(1, 100, 1, "or_greater") var ranged_var_6: int = 50

# invalid:
# @onready() var z;pass
# @onready()
# var q;
@onready @export_range(1, 100, 1, "or_greater",) var ranged_var_7: int = 50

class Foo:
	extends Node
	@onready var asd
