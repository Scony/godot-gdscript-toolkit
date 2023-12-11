func foo():
	print(r'" \' \ \\')
	print(r"\" ' \ \\")
	print(r"""aaa""")
	print(r'''bbb''')

func corner_case(r):
	for x in r:
		pass
	var rx = 1
