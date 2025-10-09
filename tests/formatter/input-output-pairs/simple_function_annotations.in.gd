func a():
	@warning_ignore("unused_variable")
	var x: Array[int] = [ 1, 2, ]

func b():
	@warning_ignore("unused_variable") var x: Array[int] = [ 1, 2, ]

func d():
	@warning_ignore("unused_variable") @warning_ignore("unused_variable") var x: Array[int] = [ 1, 2, ]

@warning_ignore("unused_parameter")
func e():
	@warning_ignore("unused_variable")
	@warning_ignore("unused_variable")
	var x: Array[int] = [ 1, 2, ]

func f():
	if true:
		@warning_ignore("unused_variable")
		@warning_ignore("unused_variable")
		var x: Array[int] = [ 1, 2, ]

func g():
	pass
	@warning_ignore("unused_variable")

func h():
	if true:
		@warning_ignore("unused_variable")

@rpc
func i():
	pass

@rpc("any_peer", "call_local")
func j():
	pass

@warning_ignore("unassigned_variable")
func k01():
	pass

@warning_ignore("unassigned_variable_op_assign")
func k02():
	pass

@warning_ignore("unused_parameter")
func k03():
	pass

@warning_ignore("shadowed_global_identifier")
func k04():
	pass

@warning_ignore("unreachable_code")
func k05():
	pass

@warning_ignore("unreachable_pattern")
func k06():
	pass

@warning_ignore("standalone_expression")
func k07():
	pass

@warning_ignore("standalone_ternary")
func k08():
	pass

@warning_ignore("incompatible_ternary")
func k09():
	pass

@warning_ignore("untyped_declaration")
func k10():
	pass

@warning_ignore("inferred_declaration")
func k11():
	pass

@warning_ignore("unsafe_property_access")
func k12():
	pass

@warning_ignore("unsafe_method_access")
func k13():
	pass

@warning_ignore("unsafe_cast")
func k14():
	pass

@warning_ignore("unsafe_call_argument")
func k15():
	pass

@warning_ignore("unsafe_void_return")
func k16():
	pass

@warning_ignore("return_value_discarded")
func k17():
	pass

@warning_ignore("static_called_on_instance")
func k18():
	pass

@warning_ignore("redundant_await")
func k19():
	pass

@warning_ignore("assert_always_true")
func k20():
	pass

@warning_ignore("assert_always_false")
func k21():
	pass

@warning_ignore("integer_division")
func k22():
	pass

@warning_ignore("narrowing_conversion")
func k23():
	pass

@warning_ignore("int_as_enum_without_cast")
func k24():
	pass

@warning_ignore("int_as_enum_without_match")
func k25():
	pass

@warning_ignore("enum_variable_without_default")
func k26():
	pass

@warning_ignore("deprecated_keyword")
func k27():
	pass

@warning_ignore("confusable_identifier")
func k28():
	pass

@warning_ignore("confusable_local_declaration")
func k29():
	pass

@warning_ignore("confusable_local_usage")
func k30():
	pass

@warning_ignore("confusable_capture_reassignment")
func k31():
	pass

@warning_ignore("inference_on_variant")
func k32():
	pass

@warning_ignore("native_method_override")
func k33():
	pass

func format_time_csec(centiseconds: int) -> String:
	centiseconds = abs(centiseconds)
	@warning_ignore_start("integer_division")
	var minutes := int(centiseconds / (100 * 60))
	var seconds := int((centiseconds / 100) % 60)
	var remainder := int(centiseconds % 100)
	@warning_ignore_restore("integer_division")
	var foo = 1
	return "%02d:%02d.%02d" % [minutes, seconds, remainder]

func k34(x):
	@warning_ignore("integer_division")
	return x / 2
