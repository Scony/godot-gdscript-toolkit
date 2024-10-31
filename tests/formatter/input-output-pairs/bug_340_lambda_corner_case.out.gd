extends Node


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	var reports := []
	var test_report: int = reports.filter(func(value: int) -> bool: return value == 42).back()
