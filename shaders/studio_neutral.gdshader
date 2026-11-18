shader_type sky;
// (pc73) The garage's showroom, seen in reflections and the ambient light: a dark neutral room with long white strip lights, as a car
// photo studio. The owner: "the car colors are super flat on pc ... the lighting and reflections need to be really good" and "the silver
// doesnt look silver at all". The earlier warm studio (cream, orange, brown) tinted every reflection: chrome and silver came out bronze,
// black paint brown, and its bright cream top flattened the colours. Here the room is near black and neutral, so paint keeps its own
// colour and depth, and the strips draw crisp highlight lines along the body that show its shape (chrome reads as chrome: white lines on
// black). Below the horizon it stays dark, so glossy black trim stays black.

uniform vec3 top_col : source_color = vec3(0.105, 0.11, 0.125);
uniform vec3 hor_col : source_color = vec3(0.2, 0.205, 0.22);
uniform vec3 bot_col : source_color = vec3(0.03, 0.03, 0.035);
uniform float strip_e = 6.0;

// a soft-edged rectangle light facing the car from direction c, half sizes hs (in tangent units)
float softbox(vec3 d, vec3 c, vec2 hs, float soft) {
	vec3 x = cross(vec3(0.0, 1.0, 0.0), c);
	x = length(x) < 0.01 ? vec3(1.0, 0.0, 0.0) : normalize(x);
	vec3 y = cross(c, x);
	float dc = dot(d, c);
	if (dc <= 0.0) return 0.0;
	vec2 p = vec2(dot(d, x), dot(d, y)) / dc;
	vec2 q = abs(p) - hs;
	return 1.0 - smoothstep(-soft, soft, max(q.x, q.y));
}

void sky() {
	vec3 d = EYEDIR;
	float h = d.y;
	vec3 c = h > 0.0 ? mix(hor_col, top_col, smoothstep(0.0, 0.6, h)) : mix(hor_col, bot_col, smoothstep(0.0, 0.18, -h));
	// a long strip overhead, along the car (x), and a wide soft panel above it
	float L = softbox(d, normalize(vec3(0.0, 1.0, 0.0)), vec2(1.6, 0.1), 0.02) * strip_e;
	L += softbox(d, normalize(vec3(0.0, 1.0, 0.0)), vec2(0.9, 0.5), 0.25) * 0.9;
	// two strips low at the sides (the long lines along the flanks), front-left and back-right
	L += softbox(d, normalize(vec3(0.55, 0.32, 1.0)), vec2(0.9, 0.05), 0.015) * strip_e * 0.8;
	L += softbox(d, normalize(vec3(-0.6, 0.3, -1.0)), vec2(0.9, 0.05), 0.015) * strip_e * 0.6;
	// a tall key panel to one side, soft
	L += softbox(d, normalize(vec3(1.0, 0.25, -0.35)), vec2(0.25, 0.45), 0.08) * 2.2;
	COLOR = c + vec3(1.0, 0.995, 0.985) * L;
}
