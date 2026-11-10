shader_type canvas_item;
// .g-view: radial-gradient(ellipse at 50% 35%, #3a2216, #1c0f0a 75%) in a box with rounded corners
uniform vec2 size_px = vec2(600.0, 400.0);
uniform float radius_px = 18.0;

void fragment() {
	vec2 c = vec2(0.5, 0.35);
	vec2 d = (UV - c) / vec2(0.5, 0.35);
	float rfc = length(vec2(0.5, 0.65) / vec2(0.5, 0.35));
	float t = clamp(length(d) / rfc / 0.75, 0.0, 1.0);
	vec3 col = mix(vec3(58.0, 34.0, 22.0) / 255.0, vec3(28.0, 15.0, 10.0) / 255.0, t);
	vec2 q = abs(UV * size_px - size_px * 0.5) - (size_px * 0.5 - radius_px);
	float dist = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - radius_px;
	COLOR = vec4(col, clamp(0.5 - dist, 0.0, 1.0));
}
