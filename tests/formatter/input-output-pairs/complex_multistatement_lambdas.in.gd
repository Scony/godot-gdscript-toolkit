func foo(x):
	pass
func bar(x,y):
	pass
func actual_params():
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

func arrays():
	var x1 = [func():
		var x = 1
		return x]
	var x2 = [func():
		var x = 1
		return x
	]
	var x3 = [func():
		var x = 1
		return x,func():
			var x = 1
			return x
	]
	var x4 = [func():
		var x = 1
		return x,
		func():
			var x = 1
			return x
	]
	var x5 = [func():
		var x = 1
		return x,

		func():
			var x = 1
			return x
	]
	var x6 = [func():
		var x = 1
		if x > 0:
			print(x),
		func():
			var x = 1
			return x
	]
	var x7 = [func():
		var x = 1
		if x > 0:
			print(x),

		func():
			var x = 1
			return x
	]

func dicts():
	var x1 = {'a':func():
		var x = 1
		return x}
	var x2 = {'a':func():
		var x = 1
		return x
	}
	var x3 = {'a':func():
		var x = 1
		return x,'b':func():
			var x = 1
			return x
	}
	var x4 = {'a':func():
		var x = 1
		return x,
		'b':func():
			var x = 1
			return x
	}
	var x5 = {'a':func():
		var x = 1
		return x,'b':
			func():
				var x = 1
				return x
	}
	var x6 = {'a':func():
		var x = 1
		return x,

		'b':func():
			var x = 1
			return x
	}
	var x7 = {'a':func():
		var x = 1
		if x > 0:
			print(x),'b':func():
			var x = 1
			return x
	}
	var x8 = {'a':func():
		var x = 1
		if x > 0:
			print(x),
		'b':func():
			var x = 1
			return x
	}
	var x9 = {'a':func():
		var x = 1
		if x > 0:
			print(x),

		'b':func():
			var x = 1
			return x
	}

func nested():
	var x1 = func():
		var x1r = func():
			var x = 1
			return x
		return x1r

	var x2 = func():
		var x2r = func():
			pass
			pass
		pass

	var x3 = func():
		var x3r = func():
			var x3rr = func():
				pass
				pass
			pass
		pass

	var x4 = func():
		if true:
			var x4r = func():
				pass
				pass
			pass
		pass

	var x5 = func():
		if true:
			var x5r = func():
				if true:
					pass
					pass
				pass
			pass
		pass

	var x6 = func():
		if true:
			var x6r = func():
				if true:
					var x6rr = func():
						pass
						pass
					pass
				pass
			pass
		pass

	# TODO: fix
	# var x7 = [func():
	# 	pass
	# 	var x = func():
	# 		pass
	# 		pass,]
