func foo(x):
	x as Node . name			# ok
	x as Node . name . size()	# nok(?)
