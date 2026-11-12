shader_type spatial;
// Stars over the Neon Cup's tracks (scripts/hd_neon.gd): a dome round the whole track, drawn behind everything.
render_mode blend_add, unshaded, cull_front, depth_draw_never, depth_test_disabled, shadows_disabled, fog_disabled;

varying vec3 dir;

float hash(vec3 p) { p = fract(p * 0.3183099 + 0.1); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }

void vertex() { dir = normalize(VERTEX); }

void fragment() {
	vec3 d = normalize(dir);
	// a grid on the dome; one star in some of its cells
	vec3 q = d * 70.0;
	vec3 c = floor(q);
	float h = hash(c);
	vec3 o = vec3(hash(c + 3.1), hash(c + 7.3), hash(c + 11.7));
	float r = length(fract(q) - 0.25 - 0.5 * o);
	float star = step(0.93, h) * smoothstep(0.3, 0.03, r) * (0.45 + 0.55 * o.z);
	float tw = 0.75 + 0.25 * sin(TIME * (1.0 + 3.0 * o.x) + 40.0 * o.y);
	ALBEDO = vec3(0.87, 0.91, 1.0) * star * tw * 1.9 * smoothstep(0.02, 0.14, d.y);
}
