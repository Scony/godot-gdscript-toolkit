func foo(x):
	pass
func bar(x,y):
	pass
func baz():
	foo(func():
		var x = 1
		return x)

	foo(func():
		var x = 1
		if x > 1:
			print(x))

	foo(func():
		var x = 1
		if x > 1:
			print(x)
	)

	bar(func():
		var x = 1
		return x, func():
			var y = 1
			return y)

	bar(func():
		var x = 1
		return x,
		func():
			var y = 1
			return y)

	bar(func():
		var x = 1
		return x,

		func():
			var y = 1
			return y)

	bar(func():
		var x = 1
		if x > 0:
			print(x), func():
			var y = 1
			return y)

	bar(func():
		var x = 1
		if x > 0:
			print(x),
		func():
			var y = 1
			return y)
