shader_type spatial;
// The web game's holographic boost pads (HOLO_PAD_FS): rainbow foil that shifts with the view, scan lines,
// forward-moving chevrons (three designs) and glowing rails along the edges.
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled, shadows_disabled;

uniform float uV = 0.0;
uniform float gain = 1.25;   // the web draws these without tone mapping; Godot tone-maps everything, so lift them a little
varying vec3 vW;

vec3 pal(float t) { return 0.5 + 0.5 * cos(6.2832 * (t + vec3(0.0, 0.33, 0.67))); }
float chev(vec2 p, float w) { return 1.0 - smoothstep(w, w + 0.035, abs(p.y - abs(p.x) * 0.9)); }

void vertex() {
	vW = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 uv = UV;
	float uT = TIME;
	float u = uv.x - 0.5;
	vec3 vd = normalize(CAMERA_POSITION_WORLD - vW);
	float ang = vd.y * 1.6 + vd.x * 0.7 + vd.z * 0.5;
	float band = uv.y * 1.4 + u * 0.6 + ang + uT * 0.25;
	vec3 foil = pal(band) * 0.85 + 0.15;
	float ridge = 0.82 + 0.18 * sin(uv.y * 90.0 + u * 30.0);
	foil *= ridge;
	float scan = 0.75 + 0.25 * step(0.5, fract(uv.y * 26.0 - uT * 2.0));
	vec3 c = mix(vec3(0.05, 0.07, 0.18), foil, 0.85) * scan;
	float d = 0.0;
	if (uV < 0.5) {
		for (int i = 0; i < 3; i++) {
			float y = fract(uv.y * 1.5 - uT * 1.6 + float(i) / 3.0);
			d = max(d, chev(vec2(u, (y - 0.5) * 1.2), 0.06));
		}
	} else if (uV < 1.5) {
		for (int i = 0; i < 2; i++) {
			float y = fract(uv.y * 1.2 - uT * 1.5 + float(i) * 0.5);
			vec2 q = vec2(abs(u) - 0.2, (y - 0.5) * 1.1);
			d = max(d, chev(q * 1.6, 0.07));
		}
		d = max(d, (1.0 - smoothstep(0.015, 0.03, abs(u))) * step(0.5, fract(uv.y * 6.0 - uT * 3.0)));
	} else {
		float z = abs(fract(uv.y * 3.0 - uT * 1.4) - 0.5) * 0.6 - 0.15;
		d = 1.0 - smoothstep(0.04, 0.07, abs(u - z));
		for (int i = 0; i < 2; i++) {
			float y = fract(uv.y * 1.3 - uT * 1.7 + float(i) * 0.5);
			d = max(d, chev(vec2(u, (y - 0.5) * 1.2) * 1.3, 0.05) * 0.8);
		}
	}
	vec3 hot = mix(vec3(1.0, 0.96, 0.75), pal(band + 0.5) * 1.2, 0.25);
	c = mix(c, hot * 1.6, d);
	float edge = 1.0 - smoothstep(0.0, 0.06, min(uv.x, 1.0 - uv.x));
	float tip = 1.0 - smoothstep(0.0, 0.05, min(uv.y, 1.0 - uv.y));
	c += vec3(1.0, 0.85, 0.4) * edge * (1.2 + 0.4 * sin(uT * 8.0));
	c += vec3(0.6, 0.9, 1.0) * tip * 0.6;
	ALBEDO = c * gain;
	ALPHA = 0.95;
}
