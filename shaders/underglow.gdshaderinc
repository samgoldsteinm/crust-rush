// (pc77, web patch 77) the underglow as LED strips under the sills and bumpers: the web's ugLs, line for line (the web works it
// out once per car into a picture; here it is worked out for each pixel of the floor or of the race's glow sheet).
// p: the point on the ground in the kart's own units from the body's centre (x forward, y = the kart's z).
// ug_p0: a, b (the body's half-length and half-width), h (the strips' height: the sill), kT (how hard a tyre blocks)
// ug_p1: wf, wr (the front and rear axles' x), wz (the wheels' z), tw (a tyre's width)
// ug_p2: rf, rr (the front and rear wheels' radius), M (the margin round the body where the light ends)
uniform vec4 ug_p0 = vec4(6.0, 2.5, 0.5, 4.0);
uniform vec4 ug_p1 = vec4(3.5, -3.5, 2.1, 0.7);
uniform vec4 ug_p2 = vec4(0.9, 0.9, 2.5, 0.0);

float ug_sm(float a, float b, float v) {
	float t = clamp((v - a) / (b - a), 0.0, 1.0);
	return t * t * (3.0 - 2.0 * t);
}

// the length of the ground ray o -> o+d inside a tyre's footprint (q: centre x, z, half-sizes x, z)
float ug_slab(vec2 o, vec2 d, vec4 q) {
	if (q.z <= 0.0) {
		return 0.0;
	}
	float t0 = 0.0;
	float t1 = 1.0;
	if (abs(d.x) < 1e-6) {
		if (abs(o.x - q.x) > q.z) {
			return 0.0;
		}
	} else {
		float u = (q.x - q.z - o.x) / d.x;
		float v = (q.x + q.z - o.x) / d.x;
		t0 = max(t0, min(u, v));
		t1 = min(t1, max(u, v));
	}
	if (abs(d.y) < 1e-6) {
		if (abs(o.y - q.y) > q.w) {
			return 0.0;
		}
	} else {
		float u = (q.y - q.w - o.y) / d.y;
		float v = (q.y + q.w - o.y) / d.y;
		t0 = max(t0, min(u, v));
		t1 = min(t1, max(u, v));
	}
	return t1 > t0 ? (t1 - t0) * length(d) : 0.0;
}

// one strip s0 -> s1 at height h facing n, in cnt pieces, each a continuous line of light (h / r^3 summed in closed form), blocked by
// the two tyres beside it: (the light, the light unblocked)
vec2 ug_strip(vec2 p, vec2 s0, vec2 s1, vec2 n, int cnt, vec4 o1, vec4 o2, float h, float kT) {
	float len = length(s1 - s0);
	if (len < 1e-4) {
		return vec2(0.0);
	}
	vec2 t = (s1 - s0) / len;
	float al = dot(p - s0, t);
	float dp = dot(p - s0, n);
	float r2 = dp * dp + h * h;
	float rho = sqrt(r2);
	float I = 0.3 + 0.7 * ug_sm(-0.5, 0.6, dp / rho);
	vec2 acc = vec2(0.0);
	float fc = float(cnt);
	for (int k = 0; k < cnt; k++) {
		float ta = float(k) * len / fc - al;
		float tb = float(k + 1) * len / fc - al;
		float e = I * h / r2 * (tb * inversesqrt(tb * tb + r2) - ta * inversesqrt(ta * ta + r2));
		vec2 sc = s0 + t * ((float(k) + 0.5) * len / fc);
		vec2 d = p - sc;
		float L = ug_slab(sc, d, o1) + ug_slab(sc, d, o2);
		acc += vec2(e * exp(-L * kT), e);
	}
	return acc;
}

float ug_ls(vec2 p) {
	float a = ug_p0.x;
	float b = ug_p0.y;
	float h = ug_p0.z;
	float kT = ug_p0.w;
	float wf = ug_p1.x;
	float wr = ug_p1.y;
	float wz = ug_p1.z;
	float tw = max(ug_p1.w, 0.2);
	float rf = ug_p2.x;
	float rr = ug_p2.y;
	float M = ug_p2.z;
	if (abs(p.x) > a + M || abs(p.y) > b + M) {
		return 0.0;
	}
	float ins = 0.08 * b;
	float zs = b - ins;
	vec4 oFp = vec4(wf, wz, rf * 0.85, tw * 0.5);
	vec4 oFm = vec4(wf, -wz, rf * 0.85, tw * 0.5);
	vec4 oRp = vec4(wr, wz, rr * 0.85, tw * 0.5);
	vec4 oRm = vec4(wr, -wz, rr * 0.85, tw * 0.5);
	float x0 = wr + rr * 1.1;
	float x1 = wf - rf * 1.1;
	vec2 acc = vec2(0.0);
	if (x1 > x0) {
		acc += ug_strip(p, vec2(x0, zs), vec2(x1, zs), vec2(0.0, 1.0), 6, oFp, oRp, h, kT);
		acc += ug_strip(p, vec2(x0, -zs), vec2(x1, -zs), vec2(0.0, -1.0), 6, oFm, oRm, h, kT);
	}
	float xF = max(wf + rf * 1.15, a - 2.0 * ins);
	float xR = min(wr - rr * 1.15, -a + 2.0 * ins);
	float zw = 0.75 * zs;
	acc += ug_strip(p, vec2(xF, -zw), vec2(xF, zw), vec2(1.0, 0.0), 4, oFp, oFm, h, kT);
	acc += ug_strip(p, vec2(xR, -zw), vec2(xR, zw), vec2(-1.0, 0.0), 4, oRp, oRm, h, kT);
	float rc = 0.3 * b;
	float Lb = 0.15 * b + 0.6 * h;
	vec2 q = abs(p) - vec2(a - rc, b - rc);
	float sd = length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0) - rc;
	float tt = acc.x * h / 1.2 + 0.22 * exp(-max(sd, 0.0) / Lb) * (0.2 + 0.8 * (acc.y > 0.0 ? acc.x / acc.y : 1.0));
	return (1.0 - exp(-1.25 * tt)) * (1.0 - ug_sm(0.5 * M, M, sd));
}
