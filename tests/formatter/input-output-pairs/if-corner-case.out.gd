func foo(Global):
	if true:
		if !(
			Global
			. current_project
			. layers[Global.current_project.current_layer]
			. can_layer_get_drawn()
		):
			return
