extends SceneTree

func _initialize() -> void:
	for material in ["basalt","limestone","sanctuary","moss","bark"]:
		var texture: Texture2D=load("res://assets/materials/%s_height.png"%material)
		var image := texture.get_image()
		if image.is_compressed():
			image.decompress()
		image.convert(Image.FORMAT_RGB8)
		# The bake spans 20 meters: restore the source's coarse stone relief.
		image.bump_map_to_normal_map(12.0)
		image.save_png("res://assets/materials/%s_normal.png"%material)
	print("Baked five portable normal maps")
	quit()
