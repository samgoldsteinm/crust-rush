shader_type spatial;
// The far mountain ranges, rebuilt finely by scripts/hd_mount.gd. A CC0 cliff texture laid over the world adds crags
// and strata, and rock shows through where the faces are steep. Green ranges keep the web's own colours (grass low
// down, rock, snow on top); the web's blue ranges (its stand-in for distance and ice) are coloured as real mountains
// instead (`natural`): grey-brown rock, snow lying on the flatter faces above a snow line, a little scrub low down,
// with the distance left to the track's fog.
render_mode cull_disabled, diffuse_burley, specular_schlick_ggx;

uniform vec3 tint = vec3(1.0);
uniform bool srgb_vc = false;
uniform float rough = 0.95;
uniform sampler2D rock : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D rock_n : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform bool has_rock = false;
uniform float scale = 0.0021;    // one repeat every ~480 units
uniform bool natural = false;
uniform float y_lo = 0.0;       // the range's foot and its highest peak (local)
uniform float y_hi = 1000.0;
uniform float snow_line = 0.6;  // where snow starts to lie, 0 foot .. 1 top
uniform float snow_cover = 0.0; // snow on the flatter faces below the line too (a frozen land)
uniform vec3 rock_dk : source_color = vec3(0.35, 0.33, 0.30);
uniform vec3 rock_lt : source_color = vec3(0.56, 0.53, 0.48);
uniform vec3 snow_col : source_color = vec3(0.94, 0.95, 0.96);
uniform vec3 veg : source_color = vec3(0.31, 0.36, 0.24);
uniform float veg_amt = 0.0;

varying vec3 wp;
varying vec3 wn;
varying float ly;

void vertex() {
	wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wn = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
	ly = VERTEX.y;
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
	if (natural) {
		float y01 = clamp((ly - y_lo) / max(y_hi - y_lo, 1.0), 0.0, 1.0);
		vec3 p = wp * scale;
		float rl = has_rock ? dot(tri(rock, p, w).rgb, vec3(0.299, 0.587, 0.114)) : 0.3;
		float big = has_rock ? dot(tri(rock, p * 0.17 + 0.31, w).rgb, vec3(0.333)) : 0.5;
		// rock: dark in the cracks, lighter on the faces, a little warmer or cooler from place to place
		vec3 rc = mix(rock_dk, rock_lt, clamp((rl - 0.12) * 2.4, 0.0, 1.0));
		rc *= mix(vec3(1.05, 1.0, 0.94), vec3(0.95, 0.98, 1.03), clamp(big * 2.0 - 0.4, 0.0, 1.0));
		// scrub on the gentle lower slopes
		float vg = veg_amt * (1.0 - smoothstep(0.1, 0.3, y01 + (big - 0.4) * 0.25)) * smoothstep(0.62, 0.85, n.y);
		vec3 base = mix(rc, veg * (0.8 + 0.5 * rl), vg);
		// snow: above the line on all but the steepest faces (steeper ones hold it the higher you go), and on a
		// frozen land the flatter faces everywhere; the cracks stay dark
		float th = mix(0.8, 0.52, y01) - snow_cover * 0.14;
		float hold = smoothstep(th - 0.1, th + 0.06, n.y);
		float above = smoothstep(snow_line - 0.12, snow_line + 0.05, y01 + (big - 0.4) * 0.22);
		float sn = max(above, snow_cover * smoothstep(th - 0.02, th + 0.14, n.y)) * hold;
		sn *= smoothstep(0.04, 0.3, rl + 0.14);
		c = mix(base, snow_col * (0.93 + 0.12 * rl), clamp(sn, 0.0, 1.0));
		vec3 tx = texture(rock_n, p.zy).xyz * 2.0 - 1.0;
		vec3 ty = texture(rock_n, p.xz).xyz * 2.0 - 1.0;
		vec3 tz = texture(rock_n, p.xy).xyz * 2.0 - 1.0;
		vec3 pert = vec3(0.0, tx.y, tx.x) * w.x + vec3(ty.x, 0.0, ty.y) * w.y + vec3(tz.x, tz.y, 0.0) * w.z;
		if (has_rock) nw = normalize(n + pert * (0.9 - 0.55 * sn));
	} else if (has_rock) {
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
