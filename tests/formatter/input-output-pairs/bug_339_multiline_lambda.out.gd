func _ready():
	var string_array: Array[String]
	var result := (
		string_array
		. map(func(a): return a)
		. filter(
			func(has_underscore):
				return has_underscore.begins_with("a") or has_underscore.begins_with("b")
		)
	)
