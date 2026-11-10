shader_type spatial;
// The far mountain ranges, rebuilt finely by scripts/hd_mount.gd. Their colours are the web's own (grass low down,
// rock on the slopes, snow on top); here a CC0 cliff texture laid over the world adds crags and strata, and rock
// shows through where the faces are steep.
render_mode cull_disabled, diffuse_burley, specular_schlick_ggx;

uniform vec3 tint = vec3(1.0);
uniform bool srgb_vc = false;
uniform float rough = 0.95;
uniform sampler2D rock : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D rock_n : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform bool has_rock = false;
uniform float scale = 0.0021;    // one repeat every ~480 units

varying vec3 wp;
varying vec3 wn;

void vertex() {
	wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wn = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
	if (srgb_vc) COLOR.rgb = pow(COLOR.rgb, vec3(2.2));
}

// three planar looks blended by the surface's direction
vec4 tri(sampler2D t, vec3 p, vec3 w) {
	return texture(t, p.zy) * w.x + texture(t, p.xz) * w.y + texture(t, p.xy) * w.z;
}

void fragment() {
	vec3 n = normalize(wn);
	vec3 w = pow(abs(n), vec3(4.0));
	w /= (w.x + w.y + w.z);
	vec3 c = COLOR.rgb * tint;
	float steep = clamp((1.0 - n.y - 0.25) * 2.2, 0.0, 1.0);
	float snowy = smoothstep(0.4, 0.7, dot(COLOR.rgb, vec3(0.2126, 0.7152, 0.0722)));
	vec3 nw = n;
	if (has_rock) {
		vec3 p = wp * scale;
		vec3 rc = tri(rock, p, w).rgb;
		float rl = dot(rc, vec3(0.299, 0.587, 0.114));
		// the rock's light and shade around the web's own colour (its hue kept), stronger on the steep faces
		float detail = mix(1.0, clamp(rl / 0.32, 0.45, 1.6), 0.55 + 0.35 * steep);
		c *= mix(detail, 1.0, snowy * 0.7);
		// bare rock showing through on steep faces
		c = mix(c, c * 0.72 + rc * 0.12 * length(c), steep * (1.0 - snowy) * 0.6);
		// crags: the texture's relief, laid on from the three directions and swizzled into the world (UDN blend)
		vec3 tx = texture(rock_n, p.zy).xyz * 2.0 - 1.0;
		vec3 ty = texture(rock_n, p.xz).xyz * 2.0 - 1.0;
		vec3 tz = texture(rock_n, p.xy).xyz * 2.0 - 1.0;
		vec3 pert = vec3(0.0, tx.y, tx.x) * w.x + vec3(ty.x, 0.0, ty.y) * w.y + vec3(tz.x, tz.y, 0.0) * w.z;
		nw = normalize(n + pert * (0.9 - 0.5 * snowy));
	}
	NORMAL = normalize((VIEW_MATRIX * vec4(nw, 0.0)).xyz);
	ALBEDO = c;
	ROUGHNESS = rough;
	SPECULAR = 0.25;
}
