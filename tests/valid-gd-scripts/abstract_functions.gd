@abstract
extends Node

@abstract func foo()

@abstract func bar() -> void

@abstract func baz(a) -> void

@abstract func bat(a: int) -> void

@abstract func bak(a: int = 6) -> void

@abstract func ban(a := 6) -> void

@abstract
func bal() -> void

@abstract func bam();

@abstract func bay() -> void;

@abstract
func bag();

@abstract func chained_a(); @abstract func chained_b() -> void;

@abstract class Inner:
	@abstract func inner_fn();
	@abstract func inner_typed() -> int;
