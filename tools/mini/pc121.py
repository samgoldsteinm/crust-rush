"""pc121: split screen's results name both players: "(P1)" and "(P2)" on their rows, both places in the title.
    python tools/mini/pc121.py"""
p = 'D:/crust-rush/godot/scripts/main.gd'
s = open(p, encoding='utf-8', newline='').read()
R = [
    ("func _result_row(place: int, k: Kart, right: String, add: String) -> Control:\n\tvar me := k == kart\n",
     "func _result_row(place: int, k: Kart, right: String, add: String) -> Control:\n\tvar me := k == kart or (split_live and k == kart2)\n"),
    ("menu.label(k.racer_name + (\"  (you)\" if me else \"\"), menu.f_bold",
     "menu.label(k.racer_name + (((\"  (P1)\" if k == kart else \"  (P2)\") if split_live and me else (\"  (you)\" if me else \"\"))), menu.f_bold"),
    ("\tvar title := \"%s place!\" % _ordinal(me_place)\n",
     "\tvar title := \"%s place!\" % _ordinal(me_place)\n"
     "\tif split_live and kart2 != null:\n"
     "\t\ttitle = \"P1 %s · P2 %s\" % [_ordinal(me_place), _ordinal(kart2.place if kart2.place > 0 else race.position_of(kart2))]\n"),
]
for a, b in R:
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc121 applied')
