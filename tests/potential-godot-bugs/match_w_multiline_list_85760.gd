func foo(x):
	match x:
		1, 2, 3:				# ok
			pass
		(4, 5, 6):				# parse error
			pass
		(
			7,					# parse error
			8,
			9
		):
			pass
