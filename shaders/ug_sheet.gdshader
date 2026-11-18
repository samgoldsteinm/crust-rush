// (pc77, web patch 77) the underglow's sheet under a racing kart: the LED strips' light (underglow.gdshaderinc) added over the ground
shader_type spatial;
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, fog_disabled, shadows_disabled;

#include "res://shaders/underglow.gdshaderinc"

uniform vec3 ug_col = vec3(1.0);   // linear, evened out by its brightness
uniform float ug_alpha = 0.1;      // faint by day, the glow at night
uniform vec2 ug_size = vec2(1.0);  // the sheet's size in the kart's units

void fragment() {
	vec2 p = (UV - 0.5) * ug_size;
	ALBEDO = ug_col * ug_ls(p) * ug_alpha;
}
