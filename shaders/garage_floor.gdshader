// (pc77, web patch 77's ugFloorMat) the garage's dark showroom floor, lit by the car's underglow: floor colour x the LED strips' light
// (underglow.gdshaderinc) added to its lighting, so the floor keeps its own look
shader_type spatial;

#include "res://shaders/underglow.gdshaderinc"

uniform sampler2D albedo_tex : source_color, filter_linear_mipmap_anisotropic;
uniform vec4 albedo_col : source_color = vec4(0.17, 0.17, 0.18, 1.0);
uniform float ug_on = 0.0;
uniform mat4 ug_inv;               // the world to the kart's own units, from the body's centre
uniform vec3 ug_col = vec3(0.0);   // linear: colour x brightness / the floor's own colour at the middle

void fragment() {
	vec3 alb = texture(albedo_tex, UV).rgb * albedo_col.rgb;
	ALBEDO = alb;
	ROUGHNESS = 0.62;
	METALLIC = 0.0;
	SPECULAR = 0.25;
	if (ug_on > 0.5) {
		vec3 wp = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
		vec2 p = (ug_inv * vec4(wp, 1.0)).xz;
		EMISSION = alb * ug_col * ug_ls(p);
	}
}
