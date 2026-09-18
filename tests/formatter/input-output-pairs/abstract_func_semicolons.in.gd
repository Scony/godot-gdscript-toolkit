@abstract
class_name Example extends Node

var myvar: bool = true;

@abstract func on_example();

@abstract func with_return() -> void;

@abstract
func split_header();

@abstract func chained_a(); @abstract func chained_b() -> int;

@abstract class Inner:
	@abstract func inner_fn();
	@abstract func inner_typed() -> String;
