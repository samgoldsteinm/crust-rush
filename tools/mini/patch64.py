"""Patch 64 (web v218): a race in which the player used no item counts in the No items records, items switched on or not.
The owner: "even if you dont turn off items, if you dont use any the race will count in the no items category. if you use one it wont, the
special ability wont effect this only using an item" (after a clean run on Basil Boulevard that was filed with items).
ITMUSED is false at every race start (resetRace, beside NOITM) and set when the PLAYER uses an item: useItem, but not when a special
ability fires one through fireItem (which passes a third argument, true); and when the player takes one into hold (holdItem: a held
item thrown later goes through fireItem, and is already counted). lbRun files the race as no-items when NOITM or !ITMUSED.
The PC: main.gd the same (itm_used, set in the player's item use, not by an ability).
Run once: py.cmd tools/mini/patch64.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 64' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("let NOITM=false;function itemsOff(){", "let NOITM=false,ITMUSED=false;/* (patch 64: did the player use an item this race) */function itemsOff(){")
rep("  NOITM=!demo&&mode!=='lss'&&mode!=='bb'&&mode!=='sb'&&(NET.cfg?!!NET.cfg.ni:!NET.role&&itemsOff());/* (patch 47) */",
    "  NOITM=!demo&&mode!=='lss'&&mode!=='bb'&&mode!=='sb'&&(NET.cfg?!!NET.cfg.ni:!NET.role&&itemsOff());/* (patch 47) */ITMUSED=false;")
rep("function useItem(k,back){\n  if(k.item&&achMe(k))achAdd('items');",
    "function useItem(k,back){\n  if(k===player&&k.item&&arguments[2]!==true)ITMUSED=true;/* (patch 64: an item the player used; an ability's fireItem does not count) */\n  if(k.item&&achMe(k))achAdd('items');")
rep("solo:karts.length===1,ni:NOITM,at:Date.now()});",
    "solo:karts.length===1,ni:NOITM||!ITMUSED/* (patch 64: no item used counts too) */,at:Date.now()});")
rep("function holdItem(k){const it=k.item;if(!it||!HOLDABLE[it]||k.held)return false;",
    "function holdItem(k){const it=k.item;if(!it||!HOLDABLE[it]||k.held)return false;if(k===player)ITMUSED=true;/* (patch 64: holding one is using it) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 64 applied')
