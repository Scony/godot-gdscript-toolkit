func foo():
	1 as int or [1, 2] == [1, 2]
	(
		1 as int
		or (
			[
				1,
				2,
			]
			== [
				1,
				2,
			]
		)
	)
	# 1 as int if true else 2 if true else 3
	# ...
	1 as int or true and true
	(
		1 as int
		or (
			[
				1,
			]
			and true
		)
	)
	not 1 in [0]
	not (
		1
		in [
			0,
		]
	)
