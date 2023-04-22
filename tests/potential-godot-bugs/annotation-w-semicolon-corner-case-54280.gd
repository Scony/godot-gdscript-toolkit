extends Node
pass;pass  # ok
@onready var x;pass  # ok
@onready;var y;pass  # no-ok
