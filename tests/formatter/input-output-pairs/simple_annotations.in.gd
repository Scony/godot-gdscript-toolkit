@tool
extends Node

var x

@onready

@export_range(1, 100, 1, "or_greater")

var ranged_var: int = 50

@onready() @export_range(1, 100, 1, "or_greater") var ranged_var_2_veryyyyyyy_loooong_naaaaaaaaaaaaaaaaaaaaaaaame: int = 50

@onready @export_range(1, 100, 1, "or_greater")
var ranged_var_3: int = 50

@onready var ranged_var_4: int = 50

class Foo:
	extends Node
	@onready var asd
	@onready var asd2
