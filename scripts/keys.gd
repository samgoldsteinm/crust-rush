class_name Keys
## Keyboard keys for every racing action (web KB_ACTS / KEYB): up to three keys each, moved to any key in
## Settings > Controls and saved on this computer. Keys are physical positions, like the web's KeyboardEvent.code,
## so they stay put on any keyboard layout. Esc always pauses unless it has been given another job.

const ACTS := [["left", "Steer left"], ["right", "Steer right"], ["brake", "Drift / brake"], ["item1", "Use first item"], ["item2", "Use second item"],
	["hold", "Keep item behind"], ["ability", "Special ability"], ["look", "Look back"], ["pause", "Pause"]]
const DEF := {"left": [KEY_LEFT, KEY_A], "right": [KEY_RIGHT, KEY_D], "brake": [KEY_SPACE, KEY_DOWN, KEY_S], "item1": [KEY_X, KEY_E, KEY_ENTER],
	"item2": [KEY_Z, KEY_Q, KEY_V], "hold": [KEY_SHIFT, KEY_B], "ability": [KEY_C, KEY_R], "look": [KEY_F], "pause": [KEY_P]}

static var bind := {}         # action -> [keycodes]
static var by_key := {}       # keycode -> action
static var wait: Array = []   # [action, slot] while Settings waits for a key


static func load_from(cf: ConfigFile) -> void:
	bind = {}
	for a in ACTS:
		var k := String(a[0])
		var v = cf.get_value("keys", k, null) if cf != null else null
		var l: Array = []
		if v is Array:
			for c in v:
				if typeof(c) == TYPE_INT and int(c) > 0 and l.size() < 3:
					l.append(int(c))
			bind[k] = l
		else:
			bind[k] = (DEF[k] as Array).duplicate()
	_index()


static func save_to(cf: ConfigFile) -> void:
	_ensure()
	for k in bind:
		cf.set_value("keys", k, bind[k])


static func _ensure() -> void:
	if bind.is_empty():
		load_from(null)


static func _index() -> void:
	by_key = {}
	for a in ACTS:
		for c in bind[String(a[0])]:
			if not by_key.has(c):
				by_key[c] = String(a[0])


static func action_of(code: int) -> String:
	_ensure()
	return String(by_key.get(code, ""))


static func held(a: String) -> bool:
	_ensure()
	for c in bind.get(a, []):
		if Input.is_physical_key_pressed(int(c)):
			return true
	return false


static func reset() -> void:
	bind = {}
	for k in DEF:
		bind[k] = (DEF[k] as Array).duplicate()
	wait = []
	_index()


## Settings: the key pressed while a box waits. Esc cancels, Backspace or Delete clears the box; a key taken from
## another action moves here. Returns true when the key was used.
static func capture(code: int) -> bool:
	if wait.is_empty():
		return false
	var a := String(wait[0])
	var i := int(wait[1])
	wait = []
	if code == KEY_ESCAPE:
		return true
	var arr: Array = (bind[a] as Array).duplicate()
	if code == KEY_BACKSPACE or code == KEY_DELETE:
		if i < arr.size():
			arr.remove_at(i)
		bind[a] = arr
		_index()
		return true
	for b in bind:
		if b != a:
			(bind[b] as Array).erase(code)
	var pos := i
	if i < arr.size():
		arr[i] = code
	else:
		arr.append(code)
		pos = arr.size() - 1
	var out: Array = []
	for j in arr.size():
		if arr[j] != code or j == pos:
			out.append(arr[j])
	bind[a] = out.slice(0, 3)
	_index()
	return true


## a key's name as the web shows it (web kbName)
static func name_of(c: int) -> String:
	match c:
		KEY_LEFT: return "←"
		KEY_RIGHT: return "→"
		KEY_UP: return "↑"
		KEY_DOWN: return "↓"
		KEY_ESCAPE: return "Esc"
		KEY_SHIFT: return "Shift"
		KEY_CTRL: return "Ctrl"
		KEY_ALT: return "Alt"
		KEY_META: return "Cmd"
		KEY_CAPSLOCK: return "Caps Lock"
		KEY_PAGEUP: return "Page Up"
		KEY_PAGEDOWN: return "Page Down"
		KEY_KP_ENTER: return "Num Enter"
	var s := OS.get_keycode_string(c)
	if s.begins_with("Kp "):
		s = "Num " + s.substr(3)
	return s


## "A, B or C" (web kbList)
static func list(a: String) -> String:
	_ensure()
	var l: Array = []
	for c in bind.get(a, []):
		l.append(name_of(int(c)))
	if l.is_empty():
		return "not set"
	if l.size() == 1:
		return String(l[0])
	return ", ".join(PackedStringArray(l.slice(0, l.size() - 1))) + " or " + String(l[l.size() - 1])
