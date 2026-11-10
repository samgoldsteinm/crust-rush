extends Node3D
## Pipeline test scene: proves the iPhone build runs on Metal before the real track arrives.
## Replaced by the race scene in the next commits.

var _box: MeshInstance3D
var _fps: Label

func _ready() -> void:
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.53, 0.75, 0.92)
	e.tonemap_mode = Environment.TONE_MAPPER_ACES
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.8, 0.75, 0.7)
	e.ambient_light_energy = 0.6
	env.environment = e
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, 30, 0)
	sun.shadow_enabled = true
	add_child(sun)
	_box = MeshInstance3D.new()
	var m := BoxMesh.new()
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.97, 0.79, 0.28)
	m.material = mat
	_box.mesh = m
	add_child(_box)
	var cam := Camera3D.new()
	cam.position = Vector3(0, 1.2, 3)
	add_child(cam)
	cam.look_at(Vector3.ZERO)
	var ui := CanvasLayer.new()
	add_child(ui)
	_fps = Label.new()
	_fps.position = Vector2(24, 24)
	_fps.add_theme_font_size_override("font_size", 28)
	ui.add_child(_fps)

func _process(dt: float) -> void:
	_box.rotate_y(dt)
	_box.rotate_x(dt * 0.6)
	_fps.text = "Crust Rush native test · %d fps · %s" % [Engine.get_frames_per_second(), RenderingServer.get_current_rendering_driver_name()]
