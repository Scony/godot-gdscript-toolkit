class X:
	func foo(result, end):
		var path: String = result.path.substr(0, end).replace("res://", "").replace("tests/", "").replace("/", " ").capitalize()

class Y extends X:
	func bar():
		pass

class Z extends X:

	func bar():
		pass
