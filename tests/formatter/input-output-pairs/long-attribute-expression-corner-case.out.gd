func foo(x):
	var path: String = (
		x
		. result
		. path
		. substr(0, 10)
		. replace("res://", "")
		. replace("tests/", "")
		. replace("", "")
		.replace("", "")
		.replace("", "")
		.replace("", "")
		.replace("", "")
		.replace("/", " ")
		.capitalize()
	)
