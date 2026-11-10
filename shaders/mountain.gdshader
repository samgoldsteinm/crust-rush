shader_type spatial;
// The sculpted background mountain (the user's own model), rebuilt finely by scripts/hd_mount.gd. Its surface comes
// from a detailed map of the full model, turned into this copy's place, scale and height; snow settles on the
// upward faces on the frozen tracks, as the web's snowify does.
render_mode cull_back, diffuse_burley, specular_schlick_ggx;

uniform sampler2D col : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
uniform sampler2D nrm : filter_linear_mipmap_anisotropic, repeat_disable;
uniform vec3 tint = vec3(1.0);
uniform vec2 ax;          // this copy's x, z change for one whole u
uniform vec2 az;          // ...and for one whole v
uniform float hs;         // its height change for a slope of 1 in the model, over one whole u or v
uniform float snow = 0.0;

void fragment() {
	vec3 n0 = texture(nrm, UV).rgb * 2.0 - 1.0;
	float ny = max(n0.y, 0.05);
	float gx = -n0.x / ny;
	float gz = -n0.z / ny;
	vec3 du = vec3(ax.x, hs * gx, ax.y);
	vec3 dv = vec3(az.x, hs * gz, az.y);
	vec3 nl = normalize(cross(dv, du));
	if (nl.y < 0.0) nl = -nl;
	vec3 nw = normalize((MODEL_MATRIX * vec4(nl, 0.0)).xyz);
	NORMAL = normalize((VIEW_MATRIX * vec4(nw, 0.0)).xyz);
	vec3 c = texture(col, UV).rgb * tint;
	if (snow > 0.0) {
		c = mix(c, vec3(0.93, 0.96, 1.0), smoothstep(0.55, 0.8, nw.y) * snow);
	}
	ALBEDO = c;
	ROUGHNESS = 0.95;
	SPECULAR = 0.3;
}
