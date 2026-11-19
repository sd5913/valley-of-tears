extends SceneTree

var checks := 0

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	if not condition:
		push_error(message)
		quit(1)
		return
	checks += 1

func run() -> void:
	var controller = load("res://scripts/free_camera.gd")
	if controller == null:
		push_error("The free-flying camera controller is missing")
		quit(1)
		return
	var camera = controller.new()
	root.add_child(camera)
	camera.set_process(false)
	camera.set_controls_active(true)
	var start: Vector3 = camera.position
	var forward: Vector3 = -camera.basis.z
	Input.action_press("move_forward")
	camera._process(0.1)
	Input.action_release("move_forward")
	check((camera.position-start).dot(forward) > 0.5, "W must move the camera forward")
	Input.action_press("move_backward")
	camera._process(0.1)
	Input.action_release("move_backward")
	check(camera.position.distance_to(start)<0.001, "S must reverse forward movement")
	Input.action_press("move_right")
	camera._process(0.1)
	Input.action_release("move_right")
	check((camera.position-start).dot(camera.basis.x)>0.5, "D must strafe right")
	Input.action_press("move_left")
	camera._process(0.1)
	Input.action_release("move_left")
	check(camera.position.distance_to(start)<0.001, "A must reverse right movement")
	Input.action_press("ascend")
	camera._process(0.1)
	Input.action_release("ascend")
	check(camera.position.y>start.y+0.5, "E must raise the camera in world space")
	Input.action_press("descend")
	camera._process(0.1)
	Input.action_release("descend")
	check(camera.position.distance_to(start)<0.001, "Q must lower the camera in world space")
	Input.action_press("move_forward")
	Input.action_press("move_right")
	camera._process(0.1)
	Input.action_release("move_forward")
	Input.action_release("move_right")
	check(absf(camera.position.distance_to(start)-camera.move_speed*0.1)<0.001, "Diagonal flight must not move faster")
	camera.reset_view()
	start=camera.position
	Input.action_press("move_forward")
	Input.action_press("boost")
	camera._process(0.1)
	Input.action_release("move_forward")
	Input.action_release("boost")
	check(camera.position.distance_to(start)>camera.move_speed*0.2, "Shift must boost movement")
	var motion := InputEventMouseMotion.new()
	motion.screen_relative=Vector2(100, -100000)
	camera._unhandled_input(motion)
	check(absf(camera.rotation.x)<=deg_to_rad(89.0)+0.001, "Mouse pitch must stay below vertical")
	camera.set_controls_active(false)
	var orientation: Vector3 = camera.rotation
	motion.screen_relative=Vector2(100,100)
	camera._unhandled_input(motion)
	check(camera.rotation.is_equal_approx(orientation), "Released mouse must not rotate the camera")
	start=camera.position
	Input.action_press("move_forward")
	camera._process(0.1)
	Input.action_release("move_forward")
	check(camera.position.is_equal_approx(start), "Released controls must not move the camera")
	camera.reset_view()
	check(camera.position.is_equal_approx(Vector3(12,17,66)), "Reset must return to the valley entrance")
	print("PASS: %d free-camera behavior checks" % checks)
	camera.free()
	quit(0)
