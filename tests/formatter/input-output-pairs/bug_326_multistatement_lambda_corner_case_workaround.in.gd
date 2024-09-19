extends Node

func _ready() -> void:
	get_tree().create_timer(1.0).timeout.connect(
		func():
			print("Hello world!")
			print("This is a bug test.")
	)
func foo():
	get_tree().create_timer(1.0).timeout.connect(
		func():
			print("Hello world!")
			return [1,]
	)
func bar():
	get_tree().create_timer(1.0).timeout.connect(func(): return [1,])
func baz(x):
	x.aaaaaaaaaaaaa.bbbbbbbbbbbb.cccccccccccccc.dddddddddddddd.eeeeeeeeeeeeee.fffffffffffff.ggggggggggggg.hhhhh(func(): return 1)
