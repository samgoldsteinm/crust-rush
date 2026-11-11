shader_type spatial;
// The web game's pictured scenery on the PC (scripts/hd_surface.gd, Finished models): the same picture and colours,
// with relief and sheen read from the picture itself. Its darker lines (the gaps between planks, mortar between bricks,
// grout, seams) sink and its lighter parts stand proud, so walls, roofs, boards and signs catch the light like real
// surfaces; darker parts are a little rougher, and a fine grain breaks up large flat areas.
render_mode blend_mix, depth_draw_opaque, CULL_MODE, diffuse_burley, specular_schlick_ggx;

uniform vec4 albedo : source_color = vec4(1.0);
uniform sampler2D tex : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D grain : hint_normal, filter_linear_mipmap, repeat_enable;
uniform vec3 uv_scale = vec3(1.0);
uniform vec3 uv_offset = vec3(0.0);
uniform bool vcol = false;
uniform float rough = 0.8;
uniform float metal = 0.0;
uniform float relief = 0.7;
uniform vec2 texel = vec2(0.001953125);

varying vec3 wp;
varying vec3 wn;

float lum(vec3 c) {
	return dot(c, vec3(0.299, 0.587, 0.114));
}

void vertex() {
	UV = UV * uv_scale.xy + uv_offset.xy;
	wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wn = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	vec4 t = texture(tex, UV);
	vec3 c = t.rgb * albedo.rgb;
	if (vcol) {
		c *= COLOR.rgb;
	}
	float l = lum(t.rgb);
	// the relief from a slightly softened picture, so speckle and print noise don't turn into grit
	vec2 e = texel * 2.5;
	float hx = lum(texture(tex, UV + vec2(e.x, 0.0), 1.5).rgb) - lum(texture(tex, UV - vec2(e.x, 0.0), 1.5).rgb);
	float hy = lum(texture(tex, UV + vec2(0.0, e.y), 1.5).rgb) - lum(texture(tex, UV - vec2(0.0, e.y), 1.5).rgb);
	// a fine grain laid over the world (triplanar by the surface's main direction)
	vec3 aw = abs(wn);
	vec2 gp = aw.y > max(aw.x, aw.z) ? wp.xz : (aw.x > aw.z ? wp.zy : wp.xy);
	vec2 g = (texture(grain, gp * 0.05).rg * 2.0 - 1.0) * 0.1;
	NORMAL_MAP = normalize(vec3(-hx * 2.4 * relief + g.x, -hy * 2.4 * relief + g.y, 1.0)) * 0.5 + 0.5;
	ALBEDO = c;
	ROUGHNESS = clamp(rough + (0.45 - l) * 0.25, 0.04, 1.0);
	METALLIC = metal;
}
