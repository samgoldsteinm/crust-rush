shader_type sky;
// The garage's surroundings, seen only in reflections and the ambient light (the panel's own background shows
// behind the car). The web's garage environment (envFrom(THEMES.kitchen.env) with its three spots): a warm
// cream ceiling, orange at the horizon, dark brown below; two white lights overhead and an orange one low behind.
// The dark below matters: glossy black trim (splitters, sills, diffusers) reflects it and stays black. The PC's
// earlier studio was bright all round, and that trim read as brown and white chrome, as if the livery stopped
// halfway down the car. One soft box overhead is kept, for the long highlight along the roof as the car turns.

uniform vec3 top_col : source_color = vec3(1.0, 0.965, 0.894);   // #fff6e4
uniform vec3 hor_col : source_color = vec3(1.0, 0.698, 0.416);   // #ffb26a
uniform vec3 low_col : source_color = vec3(0.478, 0.227, 0.11);  // #7a3a1c
uniform vec3 bot_col : source_color = vec3(0.118, 0.055, 0.031); // #1e0e08
uniform float box_e = 2.0;

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

// a round light like the web's radial spots: full at the middle, gone at `r` radians
float spot(vec3 d, vec3 c, float r) {
	float a = acos(clamp(dot(d, c), -1.0, 1.0));
	return 1.0 - smoothstep(0.0, r, a);
}

void sky() {
	vec3 d = EYEDIR;
	// the web's equirect gradient by height: v = 0 at the top, .42 just above the horizon, .55 just below, 1 at the bottom
	float v = 0.5 - asin(clamp(d.y, -1.0, 1.0)) / PI;
	vec3 c;
	if (v < 0.42) {
		c = mix(top_col, hor_col, v / 0.42);
	} else if (v < 0.55) {
		c = mix(hor_col, low_col, (v - 0.42) / 0.13);
	} else {
		c = mix(low_col, bot_col, (v - 0.55) / 0.45);
	}
	// the spots: two white ones at 62 degrees up, a quarter turn either side, an orange one low behind
	float el = radians(62.0);
	c = mix(c, vec3(1.0), spot(d, vec3(cos(el), sin(el), 0.0), 0.5));
	c = mix(c, vec3(1.0), spot(d, vec3(-cos(el), sin(el), 0.0), 0.5));
	c = mix(c, vec3(1.0, 0.541, 0.165), spot(d, normalize(vec3(0.0, -0.15, -1.0)), 0.5));
	float L = softbox(d, normalize(vec3(0.0, 1.0, 0.12)), vec2(0.6, 0.18));
	COLOR = c + vec3(1.0, 0.97, 0.92) * L * box_e;
}
