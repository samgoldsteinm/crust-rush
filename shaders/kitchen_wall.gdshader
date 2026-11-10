shader_type spatial;
// The kitchen's round wall on the PC (scripts/hd_kitchen.gd), instead of the web's flat brick: a glazed subway-tile
// backsplash above the counter (the table the track sits on) with a rounded trim tile, power outlets, warm painted
// plaster above with a soft trowelled texture, and a wooden crown moulding at the ceiling. Everything is laid out by
// the angle round the room and the height, so tiles stay square and level all the way round.
render_mode cull_disabled, diffuse_burley, specular_schlick_ggx;

uniform float radius = 3400.0;     // the wall's radius
uniform float y0 = -60.0;          // the counter top (the table)
uniform float top = 2140.0;        // the ceiling
uniform float tile_top = 240.0;    // the backsplash's height above the counter
uniform vec3 tile_col : source_color = vec3(0.94, 0.92, 0.87);
uniform vec3 grout_col : source_color = vec3(0.6, 0.56, 0.5);
uniform vec3 wall_col : source_color = vec3(0.96, 0.91, 0.82);
uniform vec3 trim_col : source_color = vec3(0.46, 0.29, 0.16);
uniform float outlet_step = 0.83;  // radians between power outlets
uniform vec4 skip = vec4(0.15, 1.75, 3.3, 4.9);   // window angles: no outlet under them

varying vec3 wp;

void vertex() {
	wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

float fbm(vec2 p) {
	return 0.5 * vnoise(p) + 0.3 * vnoise(p * 2.1) + 0.2 * vnoise(p * 4.3);
}

// distance to the nearest of the window angles, round the circle
float ang_dist(float a, float b) {
	return abs(mod(a - b + 3.14159265, 6.2831853) - 3.14159265);
}

void fragment() {
	float th = atan(wp.z, wp.x);
	float u = th * radius;
	float y = wp.y - y0;
	vec3 inward = -normalize(vec3(wp.x, 0.0, wp.z));
	vec3 tang = vec3(-sin(th), 0.0, cos(th));
	vec3 up = vec3(0.0, 1.0, 0.0);
	vec2 slope = vec2(0.0);           // relief: d(height)/du, d(height)/dy
	vec3 col;
	float rough;
	float spec = 0.5;
	if (y < 0.0) {
		col = wall_col * 0.5;
		rough = 0.9;
	} else if (y < tile_top) {
		// subway tiles 76 x 38, every other row shifted half a tile, 2.5 of grout
		float tw = 120.0;
		float tht = 60.0;
		float row = floor(y / tht);
		float uo = u + mod(row, 2.0) * tw * 0.5;
		vec2 cell = vec2(floor(uo / tw), row);
		vec2 f = vec2(fract(uo / tw) * tw, fract(y / tht) * tht);
		vec2 e = min(f, vec2(tw, tht) - f);           // to the tile's edges
		float g = 2.0;
		float grout = 1.0 - smoothstep(g, g + 0.6, min(e.x, e.y));
		// a rounded glazed edge: the face rises over the first few units from the grout
		float bev = 9.0;
		vec2 b = clamp(e / bev, 0.0, 1.0);
		vec2 dir = vec2(f.x < tw * 0.5 ? 1.0 : -1.0, f.y < tht * 0.5 ? 1.0 : -1.0);
		slope = dir * (1.0 - b) * (1.0 - b) * 0.9 * (1.0 - grout);
		float tint = hash(cell) - 0.5;
		vec3 tc = tile_col * (1.0 + tint * 0.05) + vec3(0.01, 0.005, -0.01) * tint;
		// the glaze pools a touch darker toward the edges
		tc *= 0.93 + 0.07 * min(b.x, b.y);
		col = mix(tc, grout_col * (0.9 + 0.2 * vnoise(vec2(u, y) * 0.4)), grout);
		rough = mix(0.08 + 0.06 * hash(cell + 3.1), 0.85, grout);
		spec = mix(0.6, 0.2, grout);
		// power outlets at intervals round the room, not under the windows
		float k = floor(th / outlet_step + 0.5);
		float ca = k * outlet_step;
		float near_win = min(min(ang_dist(ca, skip.x), ang_dist(ca, skip.y)), min(ang_dist(ca, skip.z), ang_dist(ca, skip.w)));
		if (near_win > 0.3) {
			vec2 o = vec2((th - ca) * radius, y - 150.0) / 1.5;
			vec2 q = abs(o) - vec2(24.0, 38.0);
			float plate = 1.0 - smoothstep(-1.0, 1.0, max(q.x, q.y));
			if (plate > 0.0) {
				vec2 sl1 = abs(o - vec2(-7.0, 12.0)) - vec2(1.6, 6.0);
				vec2 sl2 = abs(o - vec2(7.0, 12.0)) - vec2(1.6, 6.0);
				vec2 sl3 = abs(o - vec2(-7.0, -14.0)) - vec2(1.6, 6.0);
				vec2 sl4 = abs(o - vec2(7.0, -14.0)) - vec2(1.6, 6.0);
				float slot = max(max(1.0 - step(0.0, max(sl1.x, sl1.y)), 1.0 - step(0.0, max(sl2.x, sl2.y))), max(1.0 - step(0.0, max(sl3.x, sl3.y)), 1.0 - step(0.0, max(sl4.x, sl4.y))));
				vec3 pc = mix(vec3(0.95, 0.94, 0.9), vec3(0.08), slot);
				col = mix(col, pc, plate);
				rough = mix(rough, 0.35, plate);
				vec2 pe = clamp((-q) / 3.0, 0.0, 1.0);
				slope = mix(slope, sign(-o) * (1.0 - pe) * 0.6, plate);
			}
		}
	} else if (y < tile_top + 16.0) {
		// the rounded trim tile along the top
		float v = (y - tile_top) / 16.0;
		col = tile_col * (0.97 + 0.04 * sin(v * 3.14159));
		rough = 0.1;
		spec = 0.6;
		slope = vec2(0.0, cos(v * 3.14159) * 0.9);
	} else if (y > top - y0 - 70.0) {
		// a wooden crown moulding at the ceiling, with grooves
		float v = (y - (top - y0 - 70.0)) / 70.0;
		float gro = smoothstep(0.0, 0.05, abs(fract(v * 4.0) - 0.5) - 0.38);
		col = trim_col * (0.8 + 0.2 * fbm(vec2(u * 0.02, y * 0.4))) * (0.75 + 0.25 * gro);
		rough = 0.45;
		slope = vec2(0.0, (1.0 - gro) * 0.5);
	} else {
		// warm painted plaster with a soft trowelled texture
		float n = fbm(vec2(u, y) * 0.012);
		float n2 = fbm(vec2(u, y) * 0.05);
		col = wall_col * (0.94 + 0.08 * n + 0.03 * n2);
		rough = 0.88;
		spec = 0.3;
		slope = vec2(n2 - 0.5) * 0.08;
	}
	vec3 nw = normalize(inward + tang * -slope.x + up * -slope.y);
	NORMAL = normalize((VIEW_MATRIX * vec4(nw, 0.0)).xyz);
	ALBEDO = col;
	ROUGHNESS = rough;
	SPECULAR = spec;
}
