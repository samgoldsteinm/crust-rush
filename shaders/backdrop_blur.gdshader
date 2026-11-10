shader_type canvas_item;
// the web overlay's backdrop-filter: blur(6px) - the screen behind, read from a blurry mip level with a 3x3 tent
uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform float lod = 3.0;

void fragment() {
	vec2 px = SCREEN_PIXEL_SIZE * exp2(lod) * 0.8;
	vec3 c = vec3(0.0);
	float wsum = 0.0;
	for (int y = -1; y <= 1; y++) {
		for (int x = -1; x <= 1; x++) {
			float w = (x == 0 ? 2.0 : 1.0) * (y == 0 ? 2.0 : 1.0);
			c += textureLod(screen_tex, SCREEN_UV + vec2(float(x), float(y)) * px, lod).rgb * w;
			wsum += w;
		}
	}
	COLOR = vec4(c / wsum, 1.0);
}
