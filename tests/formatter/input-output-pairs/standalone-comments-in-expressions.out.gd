signal s(
	# qq1
	a,
	# ww1
	b
	# ee1
)
# TODO: change to annotation
# export(
# 	# qq2
# 	int,
# 	# ww2
# 	20
# 	# ee2
# ) var x


func foo():
	# aaa
	var x = [
		1,
		2  # bbb
		# ccc
	]
	# ddd
	var y = [
		# xxx
		1,
		2,
		3,
		[
			# yyy1
			1,
		],
		# yyy2
		4,
		# zzz
	]
	var z = {
		# qq3
		1: 2,
		# ww3
	}


func bar(
	# qq4
	a,
	# ww4
	b
	# ee4
):
	# rr4
	pass


func baz():
	bar(
		# qq5
		1,
		# ww5
		2
		# ee5
	)
