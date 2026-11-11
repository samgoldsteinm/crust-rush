shader_type spatial;
// The PC's water (scripts/hd_water.gd, Finished models): the sea, lakes and pools as real water instead of a flat
// picture. Three layers of waves drift across it and calm into the distance, so the horizon reads smooth instead
// of tiled; the colour deepens with how much water lies over the bottom (from the depth buffer); the bottom shows
// through the shallows, bent by the waves, with a soft play of light on it; the sky and sun reflect off it (more at
// a glancing angle, as real water does), and a broken line of foam laps wherever it meets the shore or a post.
render_mode blend_mix, depth_draw_always, cull_back, diffuse_burley, specular_schlick_ggx;

uniform vec3 shallow : source_color = vec3(0.16, 0.62, 0.66);
uniform vec3 deep : source_color = vec3(0.02, 0.17, 0.26);
uniform float depth_scale = 45.0;      // how much water turns it fully deep
uniform float wave_scale = 0.012;
uniform float wave_speed = 0.02;
uniform float wave_strength = 0.55;
uniform float foam_amount = 1.0;
uniform float min_depth = 0.0;         // a pool laid on the ground: as if this much water were under it
uniform sampler2D n1 : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D n2 : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D foam_tex : filter_linear_mipmap, repeat_enable;
uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform sampler2D depth_tex : hint_depth_texture, filter_linear;

varying vec3 wp;

void vertex() {
	wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

float view_z(vec2 uv, float d, mat4 inv_proj) {
#if CURRENT_RENDERER == RENDERER_COMPATIBILITY
	vec4 ndc = vec4(uv * 2.0 - 1.0, d * 2.0 - 1.0, 1.0);
#else
	vec4 ndc = vec4(uv * 2.0 - 1.0, d, 1.0);
#endif
	vec4 v = inv_proj * ndc;
	return -v.z / v.w;
}

void fragment() {
	float dist = length(VERTEX);
	float calm = mix(1.0, 0.22, smoothstep(250.0, 6000.0, dist));
	vec2 p = wp.xz * wave_scale;
	vec2 dir = vec2(1.0, 0.6) * wave_speed;
	vec3 a = texture(n1, p + TIME * dir).rgb * 2.0 - 1.0;
	vec3 b = texture(n2, p * 2.7 - TIME * dir.yx * 1.4).rgb * 2.0 - 1.0;
	vec3 c = texture(n1, mat2(vec2(0.8, -0.6), vec2(0.6, 0.8)) * p * 0.31 + TIME * dir * 0.5).rgb * 2.0 - 1.0;
	// a fine chop on top that catches the sun up close
	vec3 f = texture(n2, p * 7.3 + TIME * dir.yx * 2.1).rgb * 2.0 - 1.0;
	float near = 1.0 - smoothstep(60.0, 900.0, dist);
	vec2 slope = (a.xy * 0.5 + b.xy * 0.35 * calm + c.xy * 0.45 + f.xy * 0.22 * near) * wave_strength * calm;
	// the water lies flat, so its normal comes straight from the wave slopes in the world
	vec3 nw = normalize(vec3(-slope.x, 1.0, -slope.y));
	NORMAL = normalize((VIEW_MATRIX * vec4(nw, 0.0)).xyz);

	// how much water lies between the surface and whatever is under it
	float here = -VERTEX.z;
	float thick = max(min_depth, view_z(SCREEN_UV, texture(depth_tex, SCREEN_UV).r, INV_PROJECTION_MATRIX) - here);
	float k = clamp(thick / depth_scale, 0.0, 1.0);
	float absorb = 1.0 - exp(-3.4 * k);

	// the bottom seen through the water, bent a little by the waves (only where it is really behind the water)
	vec2 off = slope * 0.035 * clamp(thick / 8.0, 0.0, 1.0) / max(1.0, dist / 200.0);
	if (view_z(SCREEN_UV + off, texture(depth_tex, SCREEN_UV + off).r, INV_PROJECTION_MATRIX) < here) {
		off = vec2(0.0);
	}
	vec3 bottom = texture(screen_tex, SCREEN_UV + off).rgb;
	// sunlight playing on the bottom of the shallows
	float c1 = texture(foam_tex, wp.xz * 0.028 + TIME * vec2(0.013, 0.008)).r;
	float c2 = texture(foam_tex, wp.xz * 0.034 - TIME * vec2(0.009, 0.012)).r;
	float caus = pow(1.0 - abs(c1 - c2), 10.0) * (1.0 - k) * calm;
	bottom *= 1.0 + caus * 0.7;

	vec3 water = mix(shallow, deep, smoothstep(0.0, 1.0, k));
	// foam where it meets the shore, broken up and lapping
	float shore = 1.0 - smoothstep(0.0, 3.5, thick);
	float fn = texture(foam_tex, wp.xz * 0.05 + TIME * 0.02).r;
	float lap = 0.5 + 0.5 * sin(TIME * 1.3 - thick * 1.6);
	float foam = clamp(shore * smoothstep(0.35, 0.75, fn + lap * 0.35) * foam_amount, 0.0, 1.0);
	// a faint whitecap on the bigger wave crests out on open water
	foam = max(foam, smoothstep(0.55, 0.9, a.x * 0.5 + c.y * 0.5 + fn * 0.4) * 0.18 * k * calm * foam_amount);

	// water itself scatters little light back: most of its look is the bottom, the sky and the sun
	ALBEDO = mix(water * absorb * 0.6, vec3(0.92), foam);
	EMISSION = bottom * (1.0 - absorb) * mix(vec3(1.0), shallow * 1.3, 0.55) * (1.0 - foam);
	ROUGHNESS = mix(mix(0.03, 0.1, smoothstep(400.0, 5000.0, dist)), 0.6, foam);
	METALLIC = 0.0;
	SPECULAR = 0.5;
	ALPHA = 1.0;
}
