@warning_ignore("shadowed_variable")
func foo(id: int, name: String) -> void:
	self.id = id
	self.name = name

@warning_ignore("shadowed_variable_base_class")
func bar(id: int, name: String) -> void:
	self.id = id
	self.name = name
