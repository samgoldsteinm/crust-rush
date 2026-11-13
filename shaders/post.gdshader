shader_type canvas_item;
// The web game's final pass (POST.M.final) after Godot's tone mapping: tint and saturation in linear light,
// contrast in display values, the vignette, the screen-edge flash, and Ultra's speed streaks while boosting.
render_mode unshaded;

uniform sampler2D screen : hint_screen_texture, filter_linear;
uniform float sat = 1.07;
uniform float con = 1.04;
uniform vec3 tint = vec3(1.0);
uniform float vig = 0.16;
uniform vec3 edge_c = vec3(1.0);
uniform float edge_a = 0.0;
uniform float spd = 0.0;
uniform float mb = 0.0;   // motion blur (Settings): 0 off, up to about 1.8 at full boost
uniform float tm = 0.0;
uniform float rbw = 0.0;  // Neon Cup tracks: the boost streaks are rainbow (web v168)

vec3 hue(float h) { return clamp(abs(fract(h + vec3(0.0, 0.6667, 0.3333)) * 6.0 - 3.0) - 1.0, 0.0, 1.0); }

vec3 lin(vec3 c) { return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c)); }
vec3 srgb(vec3 c) { return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(vec3(0.0031308), c)); }

void fragment() {
	vec2 uv = SCREEN_UV;
	vec3 c0 = texture(screen, uv).rgb;
	float aspect0 = SCREEN_PIXEL_SIZE.y / SCREEN_PIXEL_SIZE.x;
	if (mb > 0.001) {
		// each pixel is smeared along the line from the middle of the screen, more toward the edges and with speed
		vec2 dv = uv - 0.5;
		vec2 da = dv * vec2(aspect0, 1.0);
		vec2 st = dv * mb * 0.095 * smoothstep(0.01, 0.42, dot(da, da));
		for (int i = 1; i < 8; i++) {
			c0 += texture(screen, uv - st * float(i) * 0.125).rgb;
		}
		c0 *= 0.125;
	}
	vec3 c = lin(c0);
	c = clamp(c * tint, 0.0, 1.0);
	float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
	c = mix(vec3(l), c, sat);
	// contrast round the screen's mid-grey in display (sRGB) values, as the web does since v144: done on the linear
	// colour it crushed everything darker than about #474747 to black (Basil Boulevard's dark green wallpaper)
	c = lin(clamp((srgb(clamp(c, 0.0, 1.0)) - 0.5) * con + 0.5, 0.0, 1.0));
	float aspect = SCREEN_PIXEL_SIZE.y / SCREEN_PIXEL_SIZE.x;
	vec2 d = (uv - 0.5) * vec2(aspect, 1.0);
	c *= 1.0 - vig * smoothstep(0.35, 1.05, length(d));
	vec2 e = abs(uv - 0.5) * 2.0;
	float ed = max(e.x, e.y);
	c = mix(c, edge_c, edge_a * smoothstep(0.62, 1.0, ed) * (0.55 + 0.45 * smoothstep(0.85, 1.0, ed)));
	if (spd > 0.001) {
		vec2 q = (uv - 0.5) * vec2(aspect, 1.0);
		q.y = -q.y;
		float r = length(q);
		float an = atan(q.y, q.x);
		float ln = floor(an * 48.0);
		float n = fract(sin(ln * 12.9898) * 43758.5453);
		float w = 1.0 - abs(fract(an * 48.0) - 0.5) * 2.0;
		float run = fract(r * 1.3 - tm * (2.6 + n * 1.6) + n * 9.0);
		float st = step(mix(0.7, 0.5, rbw), n) * smoothstep(mix(0.55, 0.3, rbw), 1.0, w) * smoothstep(0.0, 0.18, run) * (1.0 - smoothstep(0.18, mix(0.5, 0.7, rbw), run)) * smoothstep(mix(0.3, 0.46, rbw), mix(0.75, 0.95, rbw), r);
		// Neon tracks: the streaks are rainbow, denser and longer, over a rainbow wash at the very edge of the picture
		vec3 rb = hue(an * 0.3183 + n * 0.35 + tm * 0.25);
		c = mix(c, mix(vec3(1.0), rb * 1.15 + 0.12, rbw), st * spd * mix(0.32, 0.55, rbw));
		c += rb * rbw * spd * 0.16 * smoothstep(0.5, 1.05, r) * (0.55 + 0.45 * sin(an * 9.0 + tm * 5.0 + n * 6.0));
	}
	COLOR = vec4(srgb(c), 1.0);
}
