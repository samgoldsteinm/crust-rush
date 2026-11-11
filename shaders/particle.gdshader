shader_type spatial;
// The web game's spark pool (FXA): round glowing sprites added on top. Size = diameter in world units,
// capped on screen (the web's gl_PointSize limit) and faded when capped, exactly like its point shader.
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, fog_disabled, shadows_disabled;

uniform sampler2D tex : source_color, filter_linear, repeat_disable;
uniform bool additive = true;
// PC: a fast spark is drawn as a streak along its motion (as long as the ground it covers in a thirtieth of a
// second, up to six times its size), thinner as it stretches; a slow one stays a round glow (INSTANCE_CUSTOM = velocity)
uniform float streak = 1.0;
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
	vec3 vel = (VIEW_MATRIX * vec4(INSTANCE_CUSTOM.xyz, 0.0)).xyz;
	float vl = length(vel.xy);
	vec2 dir = vl > 0.001 ? vel.xy / vl : vec2(1.0, 0.0);
	vec2 perp = vec2(-dir.y, dir.x);
	float st = 1.0 + clamp(vl * 0.033 / max(s2, 0.001), 0.0, 5.0) * streak;
	vec2 off = dir * VERTEX.x * s2 * st + perp * VERTEX.y * s2 * mix(1.0, 0.65, clamp(st - 1.0, 0.0, 1.0));
	vec3 v = cv.xyz + vec3(off, 0.0);
	POSITION = PROJECTION_MATRIX * vec4(v, 1.0);
}

void fragment() {
	vec4 t = texture(tex, UV);
	float a = t.a * vc.a;
	if (a < 0.01) {
		discard;
	}
	// the web's colours are sRGB values used as-is; Godot's buffer is linear
	ALBEDO = pow(vc.rgb, vec3(2.2)) * t.rgb * 1.6;
	ALPHA = a;
}
