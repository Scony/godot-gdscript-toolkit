func _ready():
	print(
		"Long string with added formatting %d and %s ......................................."
		% [1, "string"]
	)
	print(
		"Long string with added formatting %d and %s ......................................."
		% [1, "string"],
		"Long string with added formatting %d and %s ......................................."
		% [1, "string"]
	)

	var very_long_variable_name1_iiiiiiiiiiiiiiiiiiiiii: int = 0
	var very_long_variable_name2_iiiiiiiiiiiiiiiiiiiiii: int = 1

	print(
		very_long_variable_name1_iiiiiiiiiiiiiiiiiiiiii
		+ very_long_variable_name2_iiiiiiiiiiiiiiiiiiiiii
	)
	print(
		very_long_variable_name1_iiiiiiiiiiiiiiiiiiiiii
		+ very_long_variable_name2_iiiiiiiiiiiiiiiiiiiiii,
		very_long_variable_name1_iiiiiiiiiiiiiiiiiiiiii
		- very_long_variable_name2_iiiiiiiiiiiiiiiiiiiiii,
		very_long_variable_name1_iiiiiiiiiiiiiiiiiiiiii
		* very_long_variable_name2_iiiiiiiiiiiiiiiiiiiiii,
		very_long_variable_name1_iiiiiiiiiiiiiiiiiiiiii
		/ very_long_variable_name2_iiiiiiiiiiiiiiiiiiiiii,
		very_long_variable_name1_iiiiiiiiiiiiiiiiiiiiii
		& very_long_variable_name2_iiiiiiiiiiiiiiiiiiiiii,
		very_long_variable_name1_iiiiiiiiiiiiiiiiiiiiii
		| very_long_variable_name2_iiiiiiiiiiiiiiiiiiiiii
	)

	var array1 = [
		"Long string with added formatting %d and %s ......................................."
		% [1, "string"],
		very_long_variable_name1_iiiiiiiiiiiiiiiiiiiiii
		+ very_long_variable_name2_iiiiiiiiiiiiiiiiiiiiii
	]
	print(array1)

	var array2 = [
		"Long string with added formatting %d and %s ......................................."
		% [1, "string"]
	]
	print(array2)

	var array3 = [
		very_long_variable_name1_iiiiiiiiiiiiiiiiiiiiii
		+ very_long_variable_name2_iiiiiiiiiiiiiiiiiiiiii
	]
	print(array3)

	var array4 = [
		very_long_variable_name1_iiiiiiiiiiiiiiiiiiiiii
		+ very_long_variable_name2_iiiiiiiiiiiiiiiiiiiiii,
	]
	print(array4)
