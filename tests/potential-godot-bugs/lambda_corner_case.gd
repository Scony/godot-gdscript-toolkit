extends Node

func foo():
	pass

func _ready() -> void:
	get_tree().create_timer(1.0).timeout.connect(foo)  # works
	get_tree().create_timer(1.0).timeout.connect(func(): foo())  # works
	get_tree().create_timer(1.0).timeout.connect(
		func():
		foo()
	)  # works
	(
		get_tree()
		. create_timer(1.0)
		. timeout
		. connect(foo)
	)  # works
	(
		get_tree()
		. create_timer(1.0)
		. timeout
		. connect(func(): foo())
	)  # works
	(
		get_tree()
		. create_timer(1.0)
		. timeout
		. connect(
			func(): foo()
		)
	)  # works
	(
		get_tree()
		. create_timer(1.0)
		. timeout
		. connect(
			func():
				foo())
	)  # works !
	(
		get_tree()
		. create_timer(1.0)
		. timeout
		. connect(
			func():
				foo()
		)
	)  # doesn't work !
