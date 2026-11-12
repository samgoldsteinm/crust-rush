shader_type spatial;
// A bed of embers under a fire (scripts/hd_fire.gd): charred lumps with glowing seams between them. The glow
// breathes slowly and unevenly, as embers do when air moves over them.
render_mode diffuse_burley, specular_disabled;

uniform float scale = 0.045;
uniform float glow = 2.6;

varying vec3 wp;

vec2 hash2(vec2 p) { return fract(sin(vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)))) * 43758.5453); }
// distance to the nearest lump's centre and to the seam between lumps
vec2 cells(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	float d1 = 9.0, d2 = 9.0;
	for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++) {
		vec2 g = vec2(float(x), float(y));
		vec2 o = hash2(i + g);
		float d = length(g + o - f);
		if (d < d1) { d2 = d1; d1 = d; } else if (d < d2) { d2 = d; }
	}
	return vec2(d1, d2 - d1);
}

void vertex() { wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }

void fragment() {
	vec2 p = wp.xz * scale;
	vec2 c = cells(p);
	vec2 c2 = cells(p * 2.9 + 4.1);
	// each lump has its own heat; it glows through its cracked crust and brightest where lumps touch
	float own = hash2(floor(p) + 0.5).x;
	float seam = 1.0 - smoothstep(0.0, 0.3, c.y);
	float crust = smoothstep(0.05, 0.35, c2.y);                  // dark ash plates on the lump
	float breathe = 0.62 + 0.38 * sin(TIME * 1.3 + p.x * 1.7 + p.y * 2.3) * sin(TIME * 0.7 + p.y * 1.1 + own * 6.0);
	float hot = (seam * 0.75 + (1.0 - crust) * 0.55 + (1.0 - c.x) * 0.3 * own) * breathe;
	ALBEDO = mix(vec3(0.05, 0.04, 0.037), vec3(0.2, 0.19, 0.18), crust * own * 0.6);   // char, with grey ash on top
	ROUGHNESS = 0.95;
	EMISSION = mix(vec3(0.75, 0.07, 0.0), vec3(1.0, 0.5, 0.1), clamp(hot - 0.5, 0.0, 1.0)) * hot * hot * glow;
}
