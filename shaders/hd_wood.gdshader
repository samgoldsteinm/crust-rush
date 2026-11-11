shader_type spatial;
// The PC's built wood (scripts/hd_set.gd): painted and bare timber drawn board by board from the model's own
// coordinates, so it needs no pictures and stays sharp up close.
//   mode 0  lap siding: horizontal boards, each tilted out at its foot with a shadow line under its lip
//   mode 1  deck planks: boards along x on the floor, with gaps and staggered end joints
//   mode 2  shingles: staggered rows of shakes, each its own shade, lifted at the bottom edge
//   mode 3  trim: plain painted timber with a fine grain
//   mode 4  painted masonry: courses of dressed stone under limewash, mottled and weathered
// Every board gets its own tint, a run of grain, and paint worn back to the wood at the edges.
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

uniform vec3 paint : source_color = vec3(0.9, 0.4, 0.6);
uniform vec3 under : source_color = vec3(0.56, 0.44, 0.32);
uniform int mode = 0;
uniform float board = 6.0;
uniform float wear = 0.25;
uniform float rough = 0.72;
uniform float tint = 0.06;
uniform bool round_u = false;   // a round tower: run the courses round it
uniform sampler2D noise : filter_linear_mipmap_anisotropic, repeat_enable;

varying vec3 op;
varying vec3 on;

float hash(float n) {
	return fract(sin(n * 127.1) * 43758.5453);
}

void vertex() {
	op = VERTEX;
	on = NORMAL;
}

void fragment() {
	vec3 n = normalize(on);
	vec3 an = abs(n);
	// u runs along the board, v across it
	float u;
	float v;
	if (mode == 1) {
		if (an.y > 0.5) {
			u = op.x;
			v = op.z;
		} else {
			u = an.x > an.z ? op.z : op.x;
			v = op.y;
		}
	} else if (mode == 3 || mode == 4) {
		if (an.y > 0.7) {
			u = op.x;
			v = op.z;
		} else {
			u = an.x > an.z ? op.z : op.x;
			v = op.y;
		}
	} else {
		u = an.x > an.z ? op.z : op.x;
		v = op.y;
	}
	if (round_u && an.y < 0.7) {
		u = atan(op.z, op.x) * length(op.xz);
	}
	float bw = board;
	float row = floor(v / bw);
	float f = fract(v / bw);
	float rnd = hash(row + 11.0);
	float col_i = 0.0;
	float cf = 0.5;
	float joint = 1.0;
	if (mode == 1) {
		// planks: staggered end joints every few metres
		float len = 60.0 + rnd * 50.0;
		float uu = u + rnd * 200.0;
		col_i = floor(uu / len);
		float jf = fract(uu / len);
		joint = smoothstep(0.0, 0.004, jf) * smoothstep(1.0, 0.996, jf);
		rnd = hash(row * 7.0 + col_i * 13.0);
	} else if (mode == 2) {
		float sw = bw * (1.1 + 0.0);
		float uu = u + row * sw * 0.5 + hash(row) * sw * 0.3;
		col_i = floor(uu / sw);
		cf = fract(uu / sw);
		rnd = hash(row * 3.1 + col_i * 17.0);
	}
	// grain along the board
	float g1 = texture(noise, vec2(u * 0.004, v * 0.09) + rnd).r;
	float g2 = texture(noise, vec2(u * 0.02, v * 0.6) + rnd * 3.0).r;
	float grain = g1 * 0.6 + g2 * 0.4;
	vec3 c = paint * (1.0 + (rnd - 0.5) * tint * 2.0);
	c *= 0.93 + grain * 0.14;
	// paint worn back to bare wood, mostly at board edges
	float edge = mode == 3 ? 0.0 : (1.0 - smoothstep(0.0, 0.12, min(f, 1.0 - f)));
	float wn = texture(noise, op.xz * 0.013 + op.y * 0.011).r;
	float worn = smoothstep(0.62, 0.8, wn * 0.85 + edge * 0.35 + g2 * 0.2) * wear;
	c = mix(c, under * (0.8 + grain * 0.4), worn);
	vec3 bend = vec3(0.0);
	float shade = 1.0;
	float r = rough;
	if (mode == 0) {
		// the board's face leans out towards its foot; a dark line under the lip of the board above
		bend = vec3(0.0, -0.18, 0.0);
		shade = mix(1.0, 0.55, smoothstep(0.86, 0.99, f)) * mix(1.08, 1.0, smoothstep(0.0, 0.06, f));
	} else if (mode == 1) {
		float gap = smoothstep(0.0, 0.05, f) * smoothstep(1.0, 0.95, f);
		shade = mix(0.35, 1.0, gap) * mix(0.45, 1.0, joint);
		r = mix(0.9, rough, gap);
	} else if (mode == 2) {
		float gap = smoothstep(0.0, 0.04, cf) * smoothstep(1.0, 0.96, cf);
		shade = mix(0.4, 1.0, gap) * mix(1.0, 0.6, smoothstep(0.82, 1.0, f)) * (0.9 + 0.2 * (1.0 - f));
		bend = vec3(0.0, -0.25 * (1.0 - f), 0.0) + vec3(hash(rnd * 9.0) - 0.5, 0.0, hash(rnd * 5.0) - 0.5) * 0.12;
	}
	if (mode == 4) {
		// courses and staggered joints of the stone under the paint, faint; the limewash mottled and streaked
		float sw = bw * 2.2;
		float uu = u + mod(row, 2.0) * sw * 0.5;
		float jf = fract(uu / sw);
		float joint4 = smoothstep(0.0, 0.012, jf) * smoothstep(1.0, 0.988, jf);
		float course = smoothstep(0.0, 0.03, f) * smoothstep(1.0, 0.97, f);
		shade = mix(0.82, 1.0, course * joint4);
		float m = texture(noise, vec2(u * 0.006, v * 0.012)).r;
		float streak = texture(noise, vec2(u * 0.05, v * 0.004)).r;
		c = paint * (0.9 + m * 0.16) * (1.0 - smoothstep(0.55, 0.85, streak) * 0.12);
		worn = 0.0;
	}
	c *= shade;
	vec3 n2 = normalize(n + bend * (1.0 - an.y) + (vec3(g2, 0.0, g1) - 0.5) * 0.06);
	if (mode == 2) {
		n2 = normalize(n + bend + (vec3(g2, 0.0, g1) - 0.5) * 0.06);
	}
	NORMAL = normalize((VIEW_MATRIX * (MODEL_MATRIX * vec4(n2, 0.0))).xyz);
	ALBEDO = c;
	ROUGHNESS = clamp(r + (1.0 - grain) * 0.08 + worn * 0.15, 0.0, 1.0);
	SPECULAR = 0.35;
}
