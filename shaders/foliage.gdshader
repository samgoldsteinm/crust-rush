shader_type spatial;
// Leaves, fronds and pine boughs of the PC build's finished trees: cut-out cards with a relief map, lit from both
// sides with the canopy's rounded normals (so a crown reads as one soft mass), a little light coming through, and a
// gentle sway in the wind that grows towards the top. Snow settles on the upward-facing parts.
render_mode cull_disabled, depth_draw_opaque, diffuse_lambert_wrap, specular_schlick_ggx;

uniform sampler2D tex : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
uniform sampler2D nrm : hint_normal, filter_linear_mipmap_anisotropic, repeat_disable;
uniform vec3 tint = vec3(1.0);
uniform float snow = 0.0;
uniform float height = 30.0;      // the plant's height, for the sway
uniform float sway = 1.0;
uniform float rough = 0.78;
uniform float cut = 0.42;

varying float vh;
varying vec3 nv;

void vertex() {
	vec3 wp = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	float k = clamp(VERTEX.y / max(1.0, height), 0.0, 1.2);
	k *= k;
	float t = TIME * 1.15 + wp.x * 0.013 + wp.z * 0.017;
	float amp = height * 0.012 * sway;
	VERTEX.x += (sin(t) * 0.8 + sin(t * 2.3 + VERTEX.y * 0.05) * 0.25) * amp * k;
	VERTEX.z += (cos(t * 0.83) * 0.6 + sin(t * 1.9 + VERTEX.x * 0.07) * 0.2) * amp * k;
	vh = VERTEX.y / max(1.0, height);
	nv = (MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz;
}

void fragment() {
	vec4 c = texture(tex, UV);
	ALPHA = c.a;
	ALPHA_SCISSOR_THRESHOLD = cut;
	ALPHA_ANTIALIASING_EDGE = cut;
	// both sides of a card use the canopy's outward normal, so a crown reads as one rounded mass
	NORMAL = normalize(nv);
	vec3 col = c.rgb * tint * COLOR.rgb;
	// a touch darker deep inside and low down, brighter at the tips
	col *= 0.78 + 0.32 * clamp(vh, 0.0, 1.0);
	if (snow > 0.0) {
		float up = clamp((dot((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz, vec3(0.0, 1.0, 0.0)) - 0.15) * 2.2, 0.0, 1.0) * snow;
		col = mix(col, vec3(0.9, 0.94, 1.0), up);
	}
	ALBEDO = col;
	NORMAL_MAP = texture(nrm, UV).rgb;
	NORMAL_MAP_DEPTH = 0.8;
	ROUGHNESS = rough;
	SPECULAR = 0.3;
	BACKLIGHT = col * 0.3;
}
