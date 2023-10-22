func foo(x):
	var path: String = (
		x
		. result
		. path
		. substr(0, 10)
		. replace("res://", "")
		. replace("tests/", "")
		. replace("", "")
		. replace("", "")
		. replace("", "")
		. replace("", "")
		. replace("", "")
		. replace("/", " ")
		. capitalize(
			1,
			2,
			3,
			4,
			6,
			7,
			8,
			9,
			10,
			11,
			12,
			13,
			14,
			15,
			16,
			17,
			18,
			19,
			20,
			21,
			22,
			23,
			24,
			25,
			26,
			27,
			28
		)
	)
	var path2 = (
		x
		. aaaa
		. bbbb
		. ccccc()
		. ddddd
		. eeee
		. ffff(
			1,
			2,
			3,
			4,
			6,
			7,
			8,
			9,
			10,
			11,
			12,
			13,
			14,
			15,
			16,
			17,
			18,
			19,
			20,
			21,
			22,
			23,
			24,
			25,
			26,
			27,
			28
		)
		. gggg()
		. hhhh
		. jjjj
	)
