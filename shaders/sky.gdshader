// The web game's sky: a gradient from horizon to top and to the bottom, with a soft sun glow.
shader_type sky;

uniform vec3 top_col : source_color = vec3(0.45, 0.62, 0.86);
uniform vec3 hor_col : source_color = vec3(0.95, 0.72, 0.58);
uniform vec3 bot_col : source_color = vec3(0.30, 0.45, 0.52);
uniform vec3 sun_col : source_color = vec3(1.0, 0.86, 0.66);
uniform float sun_disc = 1200.0;

void sky() {
	float yv = EYEDIR.y;
	vec3 c;
	if (yv >= 0.0) {
		c = mix(hor_col, top_col, pow(clamp(yv, 0.0, 1.0), 0.55));
	} else {
		c = mix(hor_col, bot_col, pow(clamp(-yv, 0.0, 1.0), 0.45));
	}
	if (LIGHT0_ENABLED) {
		float s = max(dot(EYEDIR, LIGHT0_DIRECTION), 0.0);
		c += sun_col * (pow(s, sun_disc) * 4.0 + pow(s, 16.0) * 0.22);
	}
	COLOR = c;
}
