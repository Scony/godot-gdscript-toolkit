class X:
	func foo(result, end):  # TODO: reconsider
		var path: String = result.path.substr(0, end).replace("res://", "").replace("tests/", "").replace("/", " ").capitalize()
