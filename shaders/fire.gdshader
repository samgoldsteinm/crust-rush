shader_type spatial;
// A wood fire's flames (scripts/hd_fire.gd). Each flame is a sheet that always faces the viewer round its upright
// axis; the flame itself is drawn in the sheet: tongues that narrow as they rise, torn by noise that scrolls upward,
// hottest (white-yellow) low in the middle, cooling through orange to dark red at the tips, which break off and fade.
// Several sheets of different sizes and timing stand in each fire, so it has depth and never repeats.
render_mode blend_premul_alpha, unshaded, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform float energy = 1.0;
uniform float flicker = 1.0;

varying vec2 fuv;
varying float seed;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}
float fbm(vec2 p) {
	float a = 0.5, s = 0.0;
	for (int i = 0; i < 4; i++) { s += a * noise(p); p = p * 2.03 + 17.3; a *= 0.5; }
	return s;
}

void vertex() {
	// UV2: the corner's place in its sheet (x across in world units, y up); COLOR.r: the sheet's own seed
	seed = COLOR.r;
	fuv = UV;
	vec3 cam = (inverse(MODEL_MATRIX) * vec4(CAMERA_POSITION_WORLD, 1.0)).xyz;
	vec3 to = cam - VERTEX;
	vec3 right = normalize(cross(vec3(0.0, 1.0, 0.0), vec3(to.x, 0.0, to.z) + vec3(0.0001, 0.0, 0.0)));
	// the whole flame leans and sways a little, more at the top
	float sway = sin(TIME * (1.3 + seed * 1.7) + seed * 40.0) * 0.06 + sin(TIME * 3.1 + seed * 13.0) * 0.03;
	VERTEX += right * (UV2.x + sway * UV2.y) + vec3(0.0, UV2.y, 0.0);
}

void fragment() {
	float x = fuv.x * 2.0 - 1.0;          // -1..1 across
	float y = 1.0 - fuv.y;                // 0 at the base, 1 at the tip
	float t = TIME * flicker;
	// rising turbulence: two scales, the fine one faster
	vec2 p = vec2(x * 1.6 + seed * 9.0, y * 2.6 - t * (1.5 + seed * 0.6));
	float n1 = fbm(p);
	float n2 = fbm(p * 2.3 + vec2(3.7, -t * 1.1));
	// the tongue: a rounded foot, widest a little above it, then narrowing to the tip; its middle line wanders
	float mid = (n1 - 0.5) * 0.9 * y;
	float half_w = 0.62 * mix(0.55, 1.0, smoothstep(0.0, 0.22, y)) * mix(1.0, 0.07, pow(y, 0.75));
	float d = abs(x - mid) / max(half_w, 0.001);
	float body = 1.0 - smoothstep(0.25, 1.0, d);
	// heat: full low down, falling with height; noise eats holes, more toward the tip
	float heat = body * (1.2 - y * 1.0) - (1.0 - n2) * (0.22 + 0.95 * y) * 0.85 + (n1 - 0.5) * 0.3;
	heat *= smoothstep(0.0, 0.42, y);      // the foot fades in: it starts down among the logs and embers
	heat = clamp(heat, 0.0, 1.0);
	vec3 col = mix(vec3(0.5, 0.03, 0.0), vec3(1.0, 0.24, 0.02), smoothstep(0.03, 0.3, heat));
	col = mix(col, vec3(1.0, 0.55, 0.08), smoothstep(0.28, 0.62, heat));
	col = mix(col, vec3(1.0, 0.86, 0.42), smoothstep(0.7, 1.0, heat));
	float a = smoothstep(0.02, 0.25, heat);
	// each sheet half hides what burns behind it, so a fire seen through five flames keeps its colour
	// instead of adding up to white
	ALBEDO = col * a * energy * (0.5 + 0.7 * heat);
	ALPHA = a * 0.5;
}
