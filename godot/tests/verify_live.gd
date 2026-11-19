extends SceneTree

var world: Node3D
var camera: Camera3D
var checks: Array[String]=[]
var screenshot_path := "res://godot-valley.png"

func _initialize() -> void:
	call_deferred("run")

func key(code: Key,pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode=code
	event.physical_keycode=code
	event.pressed=pressed
	Input.parse_input_event(event)

func frames(count: int) -> void:
	for i in range(count):
		await process_frame

func verify(condition: bool,message: String) -> void:
	if not condition:
		push_error(message)
		quit(1)
	checks.append(message)

func run() -> void:
	world=load("res://main.tscn").instantiate()
	root.add_child(world)
	current_scene=world
	camera=world.get_node("FreeCamera")
	if "--no-shadows" in OS.get_cmdline_user_args():
		for child in world.get_children():
			if child is Light3D:
				child.shadow_enabled=false
		screenshot_path="res://godot-no-shadows.png"
	if "--no-normals" in OS.get_cmdline_user_args():
		for material in world.materials.values():
			if material is StandardMaterial3D:
				material.normal_enabled=false
		screenshot_path="res://godot-no-normals.png"
	await frames(40)
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	verify(not image.is_empty(),"Godot produced a real rendered framebuffer")
	image.save_png(screenshot_path)
	var click := InputEventMouseButton.new()
	click.button_index=MOUSE_BUTTON_LEFT
	click.pressed=true
	click.position=root.size*0.5
	Input.parse_input_event(click)
	await frames(2)
	verify(camera.controls_active,"Click captures the flight controls")
	var start: Vector3=camera.position
	key(KEY_W,true)
	await frames(20)
	key(KEY_W,false)
	verify(camera.position.distance_to(start)>0.2,"W moves the camera in the running scene")
	var height: float=camera.position.y
	key(KEY_E,true)
	await frames(20)
	key(KEY_E,false)
	verify(camera.position.y>height+0.2,"E raises the camera in the running scene")
	key(KEY_ESCAPE,true)
	key(KEY_ESCAPE,false)
	await frames(2)
	verify(not camera.controls_active,"Esc releases the captured mouse")
	key(KEY_R,true)
	key(KEY_R,false)
	await frames(2)
	verify(camera.position.distance_to(Vector3(12,17,66))<0.001,"R restores the entrance viewpoint")
	await frames(45)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(screenshot_path)
	if screenshot_path=="res://godot-valley.png":
		camera.position=Vector3(-5,5,14)
		camera.look_at(Vector3(-2,19,-65))
		await frames(45)
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://godot-river.png")
	var file := FileAccess.open("res://live-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"checks":checks,"renderer":RenderingServer.get_current_rendering_method(),"adapter":RenderingServer.get_video_adapter_name(),"mesh_instances":world.mesh_count},"\t"))
	print("PASS: running scene, GPU rendering, and native input events")
	world.queue_free()
	await frames(3)
	quit(0)
