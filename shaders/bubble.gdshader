shader_type spatial;
// The web game's garlic shield / rush aura (bubbleShader): a see-through bubble that glows at its rim,
// with slow bands drifting up it. Added on top, never hides the kart.
render_mode unshaded, blend_add, depth_draw_never, cull_back, fog_disabled, shadows_disabled;

uniform vec3 c1 : source_color = vec3(0.435, 0.878, 0.416);
uniform vec3 c2 : source_color = vec3(0.918, 1.0, 0.847);
varying vec3 lp;

void vertex() {
	lp = VERTEX;
}

void fragment() {
	float uT = TIME;
	float f = pow(1.0 - abs(dot(normalize(NORMAL), normalize(VIEW))), 2.4);
	float b = 0.5 + 0.5 * sin(lp.y * 1.6 - uT * 4.0 + sin(lp.x * 1.1 + uT * 1.3) * 1.4);
	float hx = 0.5 + 0.5 * sin(lp.x * 3.0 + lp.z * 3.0) * sin(lp.y * 3.4 - uT * 2.0);
	float a = f * 0.95 + 0.04 + (b * 0.08 + hx * 0.05) * (0.3 + f);
	ALBEDO = mix(c1, c2, f) * a;
	ALPHA = a;
}
