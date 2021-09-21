class X:
	signal a(x, y)  # ok
	# nok:
	signal b(
		x,
		y
	)
