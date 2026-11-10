shader_type sky;
// The garage's surroundings, seen only in reflections and the ambient light (the panel's own background shows
// behind the car): a warm studio with soft-box lights overhead and to the sides, so paint, glass and chrome pick
// up long clean highlights as the car turns, as cars in a showroom do.

uniform vec3 top_col : source_color = vec3(1.0, 0.945, 0.84);
uniform vec3 hor_col : source_color = vec3(1.0, 0.85, 0.66);
uniform vec3 bot_col : source_color = vec3(0.42, 0.23, 0.12);
uniform float box_e = 5.0;

float softbox(vec3 d, vec3 c, vec2 hs) {
	vec3 x = cross(vec3(0.0, 1.0, 0.0), c);
	x = length(x) < 0.01 ? vec3(1.0, 0.0, 0.0) : normalize(x);
	vec3 y = cross(c, x);
	float dc = dot(d, c);
	if (dc <= 0.0) return 0.0;
	vec2 p = vec2(dot(d, x), dot(d, y)) / dc;
	vec2 q = abs(p) - hs;
	return 1.0 - smoothstep(-0.02, 0.04, max(q.x, q.y));
}

void sky() {
	vec3 d = EYEDIR;
	float h = d.y;
	vec3 c = h > 0.0 ? mix(hor_col, top_col, smoothstep(0.0, 0.6, h)) : mix(hor_col, bot_col, smoothstep(0.0, 0.25, -h));
	float L = softbox(d, normalize(vec3(0.0, 1.0, 0.12)), vec2(0.6, 0.18));
	L += softbox(d, normalize(vec3(1.0, 0.42, 0.35)), vec2(0.22, 0.34)) * 0.8;
	L += softbox(d, normalize(vec3(-1.0, 0.38, -0.25)), vec2(0.22, 0.34)) * 0.7;
	L += softbox(d, normalize(vec3(0.15, 0.3, -1.0)), vec2(0.45, 0.16)) * 0.55;
	COLOR = c + vec3(1.0, 0.97, 0.92) * L * box_e;
}
