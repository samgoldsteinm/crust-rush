shader_type spatial;
// Boost flames (web flameShMat, v168): a teardrop tube whose outline wavers and breaks into licks towards the tip. The colour
// runs from a blue jet at the pipe through c_b (inner) to c_a (outer) and is brighter where the view passes through more
// flame. Two of these per pipe: an outer flame and a smaller inner one (inn = 1). UV.y runs from the pipe (0) to the tip (1).
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform vec3 c_a : source_color = vec3(1.0, 0.48, 0.1);
uniform vec3 c_b : source_color = vec3(1.0, 0.94, 0.63);
uniform float inn = 0.0;
uniform float seed = 0.0;

float h2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float ns(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(h2(i), h2(i + vec2(1.0, 0.0)), f.x), mix(h2(i + vec2(0.0, 1.0)), h2(i + vec2(1.0, 1.0)), f.x), f.y);
}

void vertex() {
	float v = UV.y;
	float an = atan(VERTEX.z, VERTEX.x);
	float ft = TIME;
	float n = sin(v * 9.0 - ft * 15.0 + seed) * 0.5 + sin(v * 17.0 - ft * 24.0 + an * 3.0 + seed * 1.7) * 0.3 + sin(an * 2.0 + ft * 9.0 + seed) * 0.2;
	VERTEX.xz *= 1.0 + n * 0.34 * v;
	VERTEX.x += sin(ft * 11.0 + v * 5.0 + seed) * 0.16 * v * v;
	VERTEX.z += cos(ft * 13.0 + v * 4.0 + seed * 2.0) * 0.16 * v * v;
}

void fragment() {
	float v = UV.y;
	float ft = TIME;
	float core = pow(abs(dot(normalize(NORMAL), normalize(VIEW))), 1.4);
	float u = sin(UV.x * 6.2832) * 1.6;
	float nz = ns(vec2(u * 2.2 + seed, v * 4.5 - ft * 7.0)) * 0.65 + ns(vec2(u * 4.6 - seed, v * 9.0 - ft * 12.0)) * 0.35;
	float a = smoothstep(0.05, 0.5, core * 0.9 + (nz - 0.5) * 0.75 - v * 0.62 + 0.42) * (1.0 - smoothstep(0.72, 1.0, v));
	vec3 col = mix(c_a, c_b, clamp(core * 1.25 - v * 0.7 + 0.2, 0.0, 1.0));
	// the jet at the pipe: the outer flame thins out there so the inner one's blue shows through, as on a gas burner
	float jz = smoothstep(0.36, 0.06, v);
	col = mix(col, vec3(0.1, 0.42, 1.0) * 1.15, jz * inn);
	a *= mix(1.0, 0.04, jz * (1.0 - inn));
	col *= 1.0 + 0.25 * core;
	// the PC's tone mapping and glow brighten additive colour far more than the web's: without this the flame burns out to white
	ALBEDO = col * mix(0.8, 0.9, inn);
	ALPHA = a * mix(0.5, 0.8, inn);
}
