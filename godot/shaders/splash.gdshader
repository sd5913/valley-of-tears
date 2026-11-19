shader_type spatial;
render_mode cull_disabled, depth_draw_never, shadows_disabled;

void fragment() {
	vec2 p=(UV-0.5)*2.0;
	float radius=length(p);
	float angle=atan(p.y,p.x);
	float broken_edge=sin(angle*13.0+radius*29.0-TIME*0.7)*0.5+0.5;
	float ripples=pow(sin(radius*26.0-TIME*2.2)*0.5+0.5,8.0);
	float envelope=(1.0-smoothstep(0.25,0.95,radius))*smoothstep(0.04,0.2,radius);
	ALBEDO=vec3(0.46,0.67,0.65);
	EMISSION=vec3(0.015,0.035,0.033);
	ROUGHNESS=0.48;
	ALPHA=envelope*(ripples*0.16+broken_edge*0.04);
}
