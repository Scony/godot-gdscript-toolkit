func foo():
	var x1 = func(x):
		pass
		pass
	var x2 = func(x: int):
		return 123
		pass
	var x3 = func bar():
		pass
		123


func baz():
	var x1 = func(x):
		var y = x + 1
		if y:
			return 1
		return 2
	var x2 = func():
		if true:
			var x = 1
			if x > 0:
				return 5
			return 6
		return 7

	pass
