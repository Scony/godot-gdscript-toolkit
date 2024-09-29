func foo(new_button, button_name, menu, _game_flow):
	new_button.pressed.connect(
		func() -> void:
			var test := ""
			_game_flow.ref.request_transition(menu[button_name].transition, menu[button_name].data)
	)
