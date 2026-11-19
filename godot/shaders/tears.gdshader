shader_type spatial;
render_mode cull_disabled;

varying vec3 world_position;

void vertex() {
	world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
}

void fragment() {
	float current=sin(world_position.y*13.0+TIME*12.0+sin(world_position.x*61.0));
	float spray=0.75+0.25*sin(world_position.y*41.0+TIME*21.0);
	ALBEDO=vec3(0.38,0.69,0.72)*(0.82+current*0.1);
	EMISSION=vec3(0.12,0.28,0.29)*spray;
	METALLIC=0.22;
	ROUGHNESS=0.28;
}
