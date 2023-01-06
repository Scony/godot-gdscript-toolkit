var Logger = {}
var registry = {}


func _hash(_x):
	pass


func register(_x):
	pass


func _load_sprite_from_definition(def: Dictionary) -> void:
	for group in def["Sprite"]:
		var sprite = def["Sprite"][group]
		for field in sprite:
			match field:
				"Hframes":
					sprite["Hframes"] = int(sprite["Hframes"])
				"Vframes":
					sprite["Vframes"] = int(sprite["Vframes"])
				_:
					var defkey = _hash(sprite[field])
					if not defkey in registry["Asset"]:
						Logger.trace(
							0xf00003, "%s: Loading asset '%s'." % [def["DefKey"], sprite[field]]
						)
						register({"Schema": "Asset", "DefKey": defkey, "Path": sprite[field]})
						sprite[field] = defkey
					else:
						Logger.trace(
							0xf00004,
							"%s: Asset already loaded '%s'." % [def["DefKey"], sprite[field]]
						)
