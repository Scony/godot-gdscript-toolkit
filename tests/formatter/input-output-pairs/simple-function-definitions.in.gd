class Y:
	func _init(a, b, c):
		pass

class X:
	extends Y
	func foo(a):
		pass

	func bar(var a,b):
		pass

	func baz (a,var b=1):
		pass

	func bax (a,var b:=1):
		pass

	func bac (a,var b:int):
		pass

	func bav (a,var b:int=1):
		pass

	func _init (a,b:=1,c:int=1).(a,b,c):
		pass
