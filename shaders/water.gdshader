shader_type spatial;
// The bay's water: two layers of ripples sliding over each other, darker straight down and
// brighter at a glancing angle, glossy enough to mirror the sky and catch the low sun.
render_mode specular_schlick_ggx;

uniform vec3 shallow : source_color = vec3(0.165, 0.561, 0.69);
uniform vec3 deep : source_color = vec3(0.024, 0.22, 0.29);
uniform sampler2D nmap : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;

varying vec3 wpos;

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	// the sheet lies flat in world space
	TANGENT = vec3(1.0, 0.0, 0.0);
	BINORMAL = vec3(0.0, 0.0, 1.0);
}

void fragment() {
	vec2 uv = wpos.xz * 0.0035;
	vec3 n1 = texture(nmap, uv + TIME * vec2(0.011, 0.007)).rgb;
	vec3 n2 = texture(nmap, uv * 2.7 - TIME * vec2(0.016, 0.012)).rgb;
	vec3 n3 = texture(nmap, uv * 0.31 + TIME * vec2(0.003, -0.002)).rgb;
	NORMAL_MAP = normalize(n1 + n2 + n3 * 0.6 - vec3(1.3, 1.3, 0.0));
	NORMAL_MAP_DEPTH = 0.85;
	float fres = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 4.0);
	ALBEDO = mix(deep, shallow, 0.3 + 0.45 * fres + 0.25 * n3.b);
	EMISSION = deep * 0.12;
	ROUGHNESS = 0.07;
	METALLIC = 0.15;
	SPECULAR = 0.7;
}
