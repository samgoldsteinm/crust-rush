shader_type canvas_item;
// Text filled with a top-to-bottom gradient (the web HUD's position number and banners use
// background-clip:text with a four-stop gradient).
uniform vec4 c0 : source_color = vec4(1.0, 0.965, 0.812, 1.0);
uniform vec4 c1 : source_color = vec4(0.969, 0.788, 0.282, 1.0);
uniform vec4 c2 : source_color = vec4(1.0, 0.541, 0.122, 1.0);
uniform vec4 c3 : source_color = vec4(0.878, 0.271, 0.173, 1.0);
uniform vec3 stops = vec3(0.42, 0.78, 1.0);
uniform float y0 = 0.0;
uniform float y1 = 100.0;
varying float ly;

void vertex() {
	ly = VERTEX.y;
}

void fragment() {
	float t = clamp((ly - y0) / max(1.0, y1 - y0), 0.0, 1.0);
	vec4 g;
	if (t < stops.x) {
		g = mix(c0, c1, t / stops.x);
	} else if (t < stops.y) {
		g = mix(c1, c2, (t - stops.x) / (stops.y - stops.x));
	} else {
		g = mix(c2, c3, (t - stops.y) / max(0.001, stops.z - stops.y));
	}
	vec4 tx = texture(TEXTURE, UV);
	COLOR = vec4(g.rgb, tx.a * COLOR.a);
}
