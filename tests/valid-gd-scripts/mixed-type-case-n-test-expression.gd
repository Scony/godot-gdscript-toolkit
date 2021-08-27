func foo(x):
	print('>>>')
	print(x is int) # true
	print(x as int) # 1
	print(x as int is int) # true
	print(x is int as bool) # true
	print(x is int as bool is bool) # true
	print(1.5 as int) # 1
	print(1.5 + 1.5 as int) # 3 => as < +
	print((true and x) is bool) # true
	print(true and x is bool) # false => and < is
	print(1.5 if true else 0 as int) # 1 => as < test_expr
	print('<<<')

func _ready():
	foo(1)
