extends Node

func _ready() -> void:
	get_tree().create_timer(1.0).timeout.connect(
		func():
			print("Hello world!")
			print("This is a bug test.")
	)
