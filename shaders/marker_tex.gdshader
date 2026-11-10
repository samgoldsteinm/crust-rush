shader_type spatial;
// Glider cloth and other textures drawn in the export's marker colours: each marker becomes the
// build's paint, stripe or dark trim (the rest of the picture is kept as it is).
render_mode blend_mix, depth_draw_opaque, cull_disabled, diffuse_burley, specular_schlick_ggx;

uniform sampler2D tex : source_color, filter_linear_mipmap, repeat_enable;
uniform vec4 tint : source_color = vec4(1.0);
uniform vec3 mk_paint : source_color;
uniform vec3 mk_stripe : source_color;
uniform vec3 mk_dark : source_color;
uniform vec3 c_paint : source_color;
uniform vec3 c_stripe : source_color;
uniform vec3 c_dark : source_color;
uniform float rough = 0.62;
uniform bool double = true;

vec3 swap(vec3 c, vec3 mk, vec3 to) {
	// how much of this texel is the marker: the cloth's seams blend it with its neighbours
	float d = length(c - mk);
	return mix(c, to * (length(c) / max(length(mk), 0.001)), 1.0 - smoothstep(0.05, 0.25, d));
}

void fragment() {
	vec4 t = texture(tex, UV);
	vec3 c = t.rgb;
	c = swap(c, mk_paint, c_paint);
	c = swap(c, mk_stripe, c_stripe);
	c = swap(c, mk_dark, c_dark);
	ALBEDO = c * tint.rgb * (COLOR.rgb);
	ROUGHNESS = rough;
	if (!FRONT_FACING && double) {
		NORMAL = -NORMAL;
	}
}
