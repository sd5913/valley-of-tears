shader_type spatial;
render_mode cull_disabled;

varying vec3 world_position;
uniform sampler2D wave_height : repeat_enable, filter_linear_mipmap;

float wave(vec2 p) {
	return texture(wave_height,p*0.07+vec2(TIME*0.004,TIME*0.009)).r*0.018+
		texture(wave_height,p*0.13+vec2(-TIME*0.005,TIME*0.003)).r*0.008+
		sin(p.x*1.9+p.y*0.8-TIME*0.8)*0.004+
		sin(p.y*2.7-p.x*0.4-TIME*1.1)*0.002;
}

void vertex() {
	world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
}

void fragment() {
	vec2 p=world_position.xz;
	float dx=(wave(p+vec2(0.035,0.0))-wave(p-vec2(0.035,0.0)))/0.07;
	float dz=(wave(p+vec2(0.0,0.035))-wave(p-vec2(0.0,0.035)))/0.07;
	vec3 surface_normal=normalize(vec3(-dx,1.0,-dz));
	NORMAL=normalize(mat3(VIEW_MATRIX)*surface_normal);
	ALBEDO=vec3(0.012,0.064,0.069);
	METALLIC=0.0;
	SPECULAR=0.4;
	ROUGHNESS=0.18;
}
