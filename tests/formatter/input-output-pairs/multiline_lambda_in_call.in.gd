extends Node

var _flag := false


func _ready() -> void:
	var box := VBoxContainer.new()
	box.add_child(make_button("Continue with this long label to force gdformat wrapping", func() -> void:
		_flag = true
		print("done")))


func make_button(label: String, cb: Callable) -> Button:
	var b := Button.new()
	b.text = label
	b.pressed.connect(cb)
	return b
