extends Node
## The UNLOCK code and the style shop (web patch 70): with Ach.cheat on every style is owned, and buying one spends nothing and writes
## nothing (user://own.json and the Sandbox coins untouched). Reads only: never changes the real save. Prints UNLOCK PASS / FAIL.


func _ready() -> void:
	var S := preload("res://scripts/style.gd")
	var SB := preload("res://scripts/sandbox.gd")
	var last := S.TRIMS.size() - 1
	Ach.cheat = false
	var own0: Dictionary = S.owned()
	var locked_before: bool = own0.has("tr%d" % last) or not S.is_owned("tr", last)
	var coins0 := int(SB.load_save().get("c", 0))
	Ach.cheat = true
	var all := true
	for sl in S.SLOTS:
		for i in (S.SLOTS[sl][1] as Array).size():
			all = all and S.is_owned(sl, i)
	var bought: bool = S.buy("tr", last) and S.buy("sm", S.SMOKES.size() - 1)
	var same: bool = S.owned() == own0 and int(SB.load_save().get("c", 0)) == coins0
	Ach.cheat = false
	var ok := locked_before and all and bought and same
	print("UNLOCK %s: locked before %s, all open %s, picked %s, nothing spent or saved %s" % ["PASS" if ok else "FAIL", locked_before, all, bought, same])
	get_tree().quit(0 if ok else 1)
