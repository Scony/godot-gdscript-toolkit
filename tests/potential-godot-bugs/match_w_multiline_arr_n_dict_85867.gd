func foo(x):
	match x:
		[1, 2]:  # ok
			pass
		{"a": 1}:  # ok
			pass
		[  # Parse Error: Expected expression for match pattern.
			2,
			3
		]:
			pass
		{  # Parse Error: Expected expression as key for dictionary pattern.
			"a": 1
		}:
			pass
