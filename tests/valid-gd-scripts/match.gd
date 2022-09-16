var y
func foo(x):
	match x:
		1:
			pass
		# TODO: remove support for
		# y.aaa:
		# 	pass
		1 + 1:
			pass
		# y.zzz.aaa:
		# 	pass
		0xff9900:
			pass
		(1+1)*2+3:
			pass
		[1,2,[1,{1:2,2:var z,..,}]]:
			pass
		1 if true else 2:
			pass
		1 or 2 and 1:
			pass
		not true:
			pass
		1 < 2:
			pass
		1 | 1:
			pass
		1 >> 1:
			pass
		(1):
			pass
		"xx":
			pass
		"""xx""":
			pass
		1, 2, 3:
			pass
		1, 2 or 3, 4:
			pass
		_:
			pass
	match Vector3(1, 1+1, 2):
		Vector3(1, 1+1, 2):
			pass

func bar(x):
	match x:
		1:
			print("We are number one!")
		2:
			print("Two are better than one!")
		"test":
			print("Oh snap! It's a string!")

func baz(x):
	match typeof(x):
		TYPE_FLOAT:
			print("float")
		TYPE_STRING:
			print("text")
		TYPE_ARRAY:
			print("array")

func bax(x):
	match x:
		1:
			print("It's one!")
		2:
			print("It's one times two!")
		_:
			print("It's not 1 or 2. I don't care tbh.")

func bac(x):
	match x:
		1:
			print("It's one!")
		2:
			print("It's one times two!")
		var new_var:
			print("It's not 1 or 2, it's ", new_var)

func bav(x):
	match x:
		[]:
			print("Empty array")
		[1, 3, "test", null]:
			print("Very specific array")
		[var start, _, "test"]:
			print("First element is ", start, ", and the last is \"test\"")
		[42, ..]:
			print("Open ended array")

func bab(x):
	match x:
		{}:
			print("Empty dict")
		{"name": "Dennis"}:
			print("The name is Dennis")
		{"name": "Dennis", "age": var age}:
			print("Dennis is ", age, " years old.")
		{"name", "age"}:
			print("Has a name and an age, but it's not Dennis :(")
		{"key": "godotisawesome", ..}:
			print("I only checked for one entry and ignored the rest")

func ban(x):
	match x:
		1, 2, 3:
			print("It's 1 - 3")
		"Sword", "Splash potion", "Fist":
			print("Yep, you've taken damage")

func bad(x):
	match x:
		{"x": 1}:#, y=2}:
			pass
