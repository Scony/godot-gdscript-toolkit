extends Node

func reset_to_factory_settings(sections, section, key) -> void:
	var value = sections[section][key]
	set(key, value)
