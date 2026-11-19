extends Node3D

const RIVER_SHADER=preload("res://shaders/river.gdshader")
const TEAR_SHADER=preload("res://shaders/tears.gdshader")
const SPLASH_SHADER=preload("res://shaders/splash.gdshader")
var materials: Dictionary={}
var status_label: Label
var title_label: Label
var camera: Camera3D
var mesh_count := 0

func _ready() -> void:
	camera=$FreeCamera
	adapt_materials($EnvironmentGeometry)
	create_environment()
	create_lights()
	create_waterfall_splashes()
	create_overlay()
	camera.capture_changed.connect(update_capture_hint)
	print("Valley ready: %d mesh instances, %d adapted material types" % [mesh_count,materials.size()])

func stone_material(texture_name: String, scale: float=0.05) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_texture=load("res://assets/materials/%s_albedo.png"%texture_name)
	material.uv1_triplanar=true
	material.uv1_world_triplanar=true
	material.uv1_scale=Vector3.ONE*scale
	material.uv1_triplanar_sharpness=6.0
	material.roughness=0.87
	material.metallic_specular=0.3
	material.cull_mode=BaseMaterial3D.CULL_DISABLED
	material.normal_enabled=true
	material.normal_texture=load("res://assets/materials/%s_normal.png"%texture_name)
	material.normal_scale=0.6
	return material

func create_waterfall_splashes() -> void:
	var material := ShaderMaterial.new()
	material.shader=SPLASH_SHADER
	for point in [Vector3(-19,0.14,-39.8),Vector3(25,0.14,-77.94)]:
		var splash := MeshInstance3D.new()
		splash.name="Waterfall impact ripples"
		var plane := PlaneMesh.new()
		plane.size=Vector2(9,7)
		splash.mesh=plane
		splash.material_override=material
		splash.position=point
		splash.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(splash)

func adapted_material(original: Material) -> Material:
	var key := original.resource_name
	if materials.has(key):
		return materials[key]
	var material: Material=original
	if key.begins_with("Basalt"):
		material=stone_material("basalt")
	elif key.begins_with("Wardens"):
		material=stone_material("limestone")
	elif key.begins_with("Sanctuary"):
		material=stone_material("sanctuary")
	elif key.begins_with("Moss"):
		material=stone_material("moss",0.10)
	elif key.begins_with("Trees"):
		material=stone_material("bark",0.12)
	elif key.begins_with("River"):
		material=ShaderMaterial.new()
		material.shader=RIVER_SHADER
		material.set_shader_parameter("wave_height",load("res://assets/materials/basalt_height.png"))
	elif key.begins_with("Tears"):
		material=ShaderMaterial.new()
		material.shader=TEAR_SHADER
	elif key.begins_with("Sky"):
		material=StandardMaterial3D.new()
		material.albedo_color=Color(0.52,0.61,0.61)
		material.albedo_texture=load("res://assets/materials/limestone_albedo.png")
		material.emission_enabled=true
		material.emission=Color(0.34,0.42,0.42)
		material.emission_texture=material.albedo_texture
	materials[key]=material
	return material

func adapt_materials(node: Node) -> void:
	if node is MeshInstance3D:
		mesh_count+=1
		for surface in range(node.mesh.get_surface_count()):
			var original: Material=node.mesh.surface_get_material(surface)
			if original:
				node.set_surface_override_material(surface,adapted_material(original))
	for child in node.get_children():
		adapt_materials(child)

func create_environment() -> void:
	var environment := Environment.new()
	environment.background_mode=Environment.BG_SKY
	var sky := Sky.new()
	var atmosphere := PanoramaSkyMaterial.new()
	atmosphere.panorama=load("res://assets/materials/storm-sky.exr")
	sky.sky_material=atmosphere
	environment.sky=sky
	environment.ambient_light_source=Environment.AMBIENT_SOURCE_SKY
	environment.ambient_light_color=Color(0.38,0.52,0.59)
	environment.ambient_light_energy=0.7
	environment.reflected_light_source=Environment.REFLECTION_SOURCE_SKY
	environment.tonemap_mode=Environment.TONE_MAPPER_FILMIC
	environment.tonemap_exposure=1.0
	environment.fog_enabled=true
	environment.fog_light_color=Color(0.28,0.40,0.43)
	environment.fog_density=0.0015
	environment.fog_sky_affect=0.35
	if DisplayServer.get_name()=="headless":
		pass
	elif RenderingServer.get_current_rendering_method()=="gl_compatibility":
		environment.ssao_enabled=true
	else:
		environment.ssao_enabled=true
		environment.ssao_radius=2.0
		environment.ssao_intensity=1.4
		environment.ssr_enabled=true
		environment.ssr_max_steps=96
		environment.ssr_depth_tolerance=0.5
		environment.glow_enabled=true
		environment.glow_intensity=0.35
		environment.volumetric_fog_enabled=true
		environment.volumetric_fog_density=0.0015
		environment.volumetric_fog_albedo=Color(0.43,0.58,0.60)
		environment.volumetric_fog_length=210
	var world := WorldEnvironment.new()
	world.environment=environment
	add_child(world)
	if DisplayServer.get_name()!="headless":
		var reflection := ReflectionProbe.new()
		reflection.name="Valley and sky reflected in the river"
		reflection.position=Vector3(0,12,-40)
		reflection.size=Vector3(150,100,300)
		reflection.max_distance=350
		reflection.box_projection=false
		# Sky supplies diffuse light; the probe supplies only local reflections.
		reflection.ambient_mode=ReflectionProbe.AMBIENT_DISABLED
		reflection.intensity=0.7
		add_child(reflection)
		for specification in [[Vector3(-19,1.5,-39),Vector3(14,4,8)],[Vector3(25,1.8,-78),Vector3(14,5,8)],[Vector3(3,0.8,-59),Vector3(24,2,9)]]:
			var mist := FogVolume.new()
			mist.name="Waterfall spray"
			mist.shape=RenderingServer.FOG_VOLUME_SHAPE_ELLIPSOID
			mist.position=specification[0]
			mist.size=specification[1]
			var spray := FogMaterial.new()
			spray.density=0.06
			spray.albedo=Color(0.55,0.71,0.72)
			spray.edge_fade=0.45
			mist.material=spray
			add_child(mist)

func create_lights() -> void:
	var sun := DirectionalLight3D.new()
	sun.name="Last sunlight"
	sun.rotation_degrees=Vector3(-18,-170,0)
	sun.light_color=Color(0.97,0.88,0.70)
	sun.light_energy=1.1
	sun.light_specular=0.0
	sun.shadow_enabled=true
	sun.directional_shadow_mode=DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
	sun.directional_shadow_max_distance=180
	sun.shadow_bias=0.04
	sun.shadow_normal_bias=1.5
	sun.light_angular_distance=6.0
	sun.shadow_opacity=0.7
	add_child(sun)
	var fill := DirectionalLight3D.new()
	fill.name="Cool light from the open river"
	fill.rotation_degrees=Vector3(-32,-48,0)
	fill.light_color=Color(0.48,0.69,0.85)
	fill.light_energy=0.85
	add_child(fill)
	var bounce := DirectionalLight3D.new()
	bounce.name="Diffuse river bounce"
	bounce.rotation_degrees=Vector3(-15,55,0)
	bounce.light_color=Color(0.42,0.66,0.68)
	bounce.light_energy=0.12
	add_child(bounce)
	var file := FileAccess.open("res://assets/source-manifest.json",FileAccess.READ)
	var manifest: Dictionary=JSON.parse_string(file.get_as_text())
	for original in manifest.point_lights:
		var light := OmniLight3D.new()
		light.name=original.name
		light.position=Vector3(original.position[0],original.position[1],original.position[2])
		light.light_color=Color(original.color[0],original.color[1],original.color[2])
		light.light_energy=3.0 if original.power>100 else 1.8
		light.omni_range=10.0 if original.power>100 else 5.0
		light.shadow_enabled=true
		add_child(light)

func create_overlay() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left",28)
	margin.add_theme_constant_override("margin_top",24)
	margin.add_theme_constant_override("margin_right",28)
	margin.add_theme_constant_override("margin_bottom",24)
	margin.mouse_filter=Control.MOUSE_FILTER_IGNORE
	layer.add_child(margin)
	var column := VBoxContainer.new()
	column.mouse_filter=Control.MOUSE_FILTER_IGNORE
	margin.add_child(column)
	title_label=Label.new()
	title_label.text="VALLEY OF TEARS"
	title_label.add_theme_font_size_override("font_size",25)
	title_label.add_theme_color_override("font_color",Color(0.9,0.91,0.80))
	title_label.add_theme_color_override("font_shadow_color",Color(0.01,0.025,0.03,0.9))
	title_label.add_theme_constant_override("shadow_offset_x",2)
	title_label.add_theme_constant_override("shadow_offset_y",2)
	column.add_child(title_label)
	var subtitle := Label.new()
	subtitle.text="THE WEEPING WARDENS"
	subtitle.add_theme_font_size_override("font_size",12)
	subtitle.modulate=Color(0.68,0.78,0.74)
	column.add_child(subtitle)
	var spacer := Control.new()
	spacer.size_flags_vertical=Control.SIZE_EXPAND_FILL
	spacer.mouse_filter=Control.MOUSE_FILTER_IGNORE
	column.add_child(spacer)
	status_label=Label.new()
	status_label.add_theme_font_size_override("font_size",15)
	status_label.add_theme_color_override("font_shadow_color",Color(0.01,0.02,0.025,1))
	status_label.add_theme_constant_override("shadow_offset_x",1)
	status_label.add_theme_constant_override("shadow_offset_y",1)
	column.add_child(status_label)
	update_capture_hint(false)

func update_capture_hint(active: bool) -> void:
	status_label.text=("WASD  Move   E / Space  Rise   Q / Ctrl  Descend   Shift  Faster   Wheel  Speed   R  Reset   Esc  Release mouse" if active else "Click to explore   |   WASD + mouse   |   E / Q rise and descend   |   R resets the view")
