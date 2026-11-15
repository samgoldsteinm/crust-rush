// The web game's sky: a gradient from horizon to top and to the bottom, with a soft sun glow.
shader_type sky;

uniform vec3 top_col : source_color = vec3(0.45, 0.62, 0.86);
uniform vec3 hor_col : source_color = vec3(0.95, 0.72, 0.58);
uniform vec3 bot_col : source_color = vec3(0.30, 0.45, 0.52);
uniform vec3 sun_col : source_color = vec3(1.0, 0.86, 0.66);
uniform float sun_disc = 1200.0;
// Sandbox's night (scripts/sandbox_clock.gd): 0 none, up to about 1 at midnight
uniform float stars = 0.0;

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
	if (stars > 0.001 && yv > 0.04) {
		// small points scattered over the sky: one in a few hundred cells of a fine grid of directions lit, each a little different
		vec2 g = vec2(atan(EYEDIR.z, EYEDIR.x) * 260.0, yv * 260.0);
		vec2 cell = floor(g);
		float h = fract(sin(dot(cell, vec2(12.9898, 78.233))) * 43758.5453);
		vec2 fp = fract(g) - 0.5;
		float pt = smoothstep(0.32, 0.0, length(fp));
		c += vec3(0.93, 0.95, 1.0) * step(0.994, h) * pt * stars * smoothstep(0.04, 0.2, yv) * (0.6 + 0.4 * fract(h * 97.0));
	}
	// the web sky is drawn without tone mapping; this keeps it as bright after Godot's
	COLOR = c * 1.2;
}
