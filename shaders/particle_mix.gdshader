shader_type spatial;
// The web game's smoke and dust pool (FXN): soft round puffs, normal blending, sized like particle.gdshader.
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled, shadows_disabled;

uniform sampler2D tex : source_color, filter_linear, repeat_disable;
varying vec4 vc;

void vertex() {
	vec4 cv = MODELVIEW_MATRIX * vec4(0.0, 0.0, 0.0, 1.0);
	float s = length(MODEL_MATRIX[0].xyz);
	float depth = max(0.5, -cv.z);
	float scale_px = VIEWPORT_SIZE.y * PROJECTION_MATRIX[1][1] * 0.5;
	float max_px = max(28.0, VIEWPORT_SIZE.y * 0.12);
	float ps = s * scale_px / depth;
	vc = COLOR;
	vc.a *= clamp(max_px * 1.6 / max(ps, 0.001), 0.25, 1.0);
	float s2 = min(ps, max_px) * depth / scale_px;
	vec3 v = cv.xyz + vec3(VERTEX.xy * s2, 0.0);
	POSITION = PROJECTION_MATRIX * vec4(v, 1.0);
}

void fragment() {
	vec4 t = texture(tex, UV);
	float a = t.a * vc.a;
	if (a < 0.01) {
		discard;
	}
	ALBEDO = pow(vc.rgb, vec3(2.2)) * t.rgb;
	ALPHA = a;
}
