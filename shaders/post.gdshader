shader_type canvas_item;
// The web game's final pass (POST.M.final) after Godot's tone mapping: tint, saturation and contrast
// in linear light, the vignette, the screen-edge flash, and Ultra's speed streaks while boosting.
render_mode unshaded;

uniform sampler2D screen : hint_screen_texture, filter_linear;
uniform float sat = 1.07;
uniform float con = 1.04;
uniform vec3 tint = vec3(1.0);
uniform float vig = 0.16;
uniform vec3 edge_c = vec3(1.0);
uniform float edge_a = 0.0;
uniform float spd = 0.0;
uniform float tm = 0.0;

vec3 lin(vec3 c) { return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c)); }
vec3 srgb(vec3 c) { return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(vec3(0.0031308), c)); }

void fragment() {
	vec2 uv = SCREEN_UV;
	vec3 c = lin(texture(screen, uv).rgb);
	c = clamp(c * tint, 0.0, 1.0);
	float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
	c = mix(vec3(l), c, sat);
	c = clamp((c - 0.5) * con + 0.5, 0.0, 1.0);
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
		float st = step(0.7, n) * smoothstep(0.55, 1.0, w) * smoothstep(0.0, 0.18, run) * (1.0 - smoothstep(0.18, 0.5, run)) * smoothstep(0.3, 0.75, r);
		c = mix(c, vec3(1.0), st * spd * 0.32);
	}
	COLOR = vec4(srgb(c), 1.0);
}
