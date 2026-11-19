extends Camera3D

signal capture_changed(active: bool)

@export var move_speed := 12.0
@export var boost_multiplier := 3.0
@export var mouse_sensitivity := 0.0022
var controls_active := false
var yaw := 0.0
var pitch := 0.0

const BINDINGS := {
	"move_forward": [KEY_W], "move_backward": [KEY_S],
	"move_left": [KEY_A], "move_right": [KEY_D],
	"ascend": [KEY_E, KEY_SPACE, KEY_UP],
	"descend": [KEY_Q, KEY_CTRL, KEY_DOWN], "boost": [KEY_SHIFT]
}

func _ready() -> void:
	for action in BINDINGS:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
			for code in BINDINGS[action]:
				var key := InputEventKey.new()
				key.physical_keycode=code
				InputMap.action_add_event(action,key)
	fov=39.0
	far=1200.0
	near=0.1
	reset_view()
	get_window().focus_exited.connect(func(): set_controls_active(false))

func reset_view() -> void:
	position=Vector3(12,17,66)
	look_at(Vector3(-1,21,-65))
	yaw=rotation.y
	pitch=rotation.x

func set_controls_active(active: bool) -> void:
	controls_active=active
	if DisplayServer.get_name()!="headless":
		Input.mouse_mode=Input.MOUSE_MODE_CAPTURED if active else Input.MOUSE_MODE_VISIBLE
	capture_changed.emit(active)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode==KEY_ESCAPE:
			set_controls_active(false)
		elif event.keycode==KEY_R:
			reset_view()
	if event is InputEventMouseButton and event.pressed:
		if event.button_index==MOUSE_BUTTON_LEFT:
			set_controls_active(true)
		elif event.button_index==MOUSE_BUTTON_WHEEL_UP:
			move_speed=minf(move_speed*1.25,80.0)
		elif event.button_index==MOUSE_BUTTON_WHEEL_DOWN:
			move_speed=maxf(move_speed/1.25,1.0)
	if event is InputEventMouseMotion and controls_active:
		yaw-=event.screen_relative.x*mouse_sensitivity
		pitch=clampf(pitch-event.screen_relative.y*mouse_sensitivity,deg_to_rad(-89),deg_to_rad(89))
		rotation=Vector3(pitch,yaw,0)

func _process(delta: float) -> void:
	if not controls_active:
		return
	var input := Input.get_vector("move_left","move_right","move_forward","move_backward")
	var direction := basis.x*input.x+basis.z*input.y
	direction+=Vector3.UP*Input.get_axis("descend","ascend")
	var speed := move_speed*(boost_multiplier if Input.is_action_pressed("boost") else 1.0)
	position+=direction.limit_length()*speed*delta
