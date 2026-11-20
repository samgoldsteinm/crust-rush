// The web game's sky: a gradient from horizon to top and to the bottom, with a soft sun glow.
shader_type sky;

uniform vec3 top_col : source_color = vec3(0.45, 0.62, 0.86);
uniform vec3 hor_col : source_color = vec3(0.95, 0.72, 0.58);
uniform vec3 bot_col : source_color = vec3(0.30, 0.45, 0.52);
uniform vec3 sun_col : source_color = vec3(1.0, 0.86, 0.66);
uniform float sun_disc = 1200.0;
// Sandbox's night (scripts/sandbox_clock.gd): 0 none, up to about 1 at midnight
uniform float stars = 0.0;
// (pc112) the web's reflection picture (envFrom): a 512x256 panorama, gradient stops at 0 .42 .55 1 down the picture, round
// lights (x, y, radius in its pixels; colour) fading out to their edge; drawn only into the reflections
uniform bool env_on = false;
uniform vec3 env0 = vec3(1.0);
uniform vec3 env1 = vec3(1.0);
uniform vec3 env2 = vec3(0.5);
uniform vec3 env3 = vec3(0.1);
uniform vec4 spot0 = vec4(0.0);
uniform vec4 spot1 = vec4(0.0);
uniform vec4 spot2 = vec4(0.0);
uniform vec3 spot_c0 = vec3(1.0);
uniform vec3 spot_c1 = vec3(1.0);
uniform vec3 spot_c2 = vec3(1.0);

vec3 lin(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(0.04045, c));
}

vec3 spot(vec3 base, vec2 px, vec4 s, vec3 col) {
	if (s.z <= 0.0) {
		return base;
	}
	vec2 d = px - s.xy;
	d.x = mod(d.x + 256.0, 512.0) - 256.0;   // (round the panorama)
	float a = clamp(1.0 - length(d) / s.z, 0.0, 1.0);
	return mix(base, col, a);
}

vec3 env_pic(vec3 d) {
	float px = (atan(d.z, d.x) / (2.0 * PI) + 0.5) * 512.0;
	float py = (0.5 - asin(clamp(d.y, -1.0, 1.0)) / PI) * 256.0;
	float t = py / 256.0;
	vec3 c = t < 0.42 ? mix(env0, env1, t / 0.42) : (t < 0.55 ? mix(env1, env2, (t - 0.42) / 0.13) : mix(env2, env3, (t - 0.55) / 0.45));
	c = spot(c, vec2(px, py), spot0, spot_c0);
	c = spot(c, vec2(px, py), spot1, spot_c1);
	c = spot(c, vec2(px, py), spot2, spot_c2);
	return lin(c);
}

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
	if (env_on && AT_CUBEMAP_PASS) {
		COLOR = env_pic(EYEDIR);   // (pc112) what the gloss shows: the web's reflection picture
	}
}
