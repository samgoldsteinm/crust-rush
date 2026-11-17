"""Patch 59 (web v215): the mechanic's shop in a room's Sandbox brings you back; the room screen can take you back into Sandbox.
The owner (two PCs on the web app, the friend the guest, in Sandbox): "when he enters the garage and changes something it takes him to this
screen but wont load him back into the game. we should add a load into the game button or it should just load them in automatically after
going through the garage menu". The shop opens the driver and garage screens through toMenu(); in a room toMenu also put the room's screen
up 60 ms later (for leaving a room's Sandbox), over the garage, and the room screen had no way back into Sandbox. Now:
- the garage's last button asks the shop first (it asked "a room's guest?" first and went to the room's screen: THE fault);
- toMenu leaves the room's screen down when it is the shop (SB.shopBack): the garage's "Back to Sandbox" brings you out of the shop door;
- the room's screen, while the room is in Sandbox (NET.sbx), has a "Back to Sandbox" button (host and guest): back in where the host is
  (a guest: the host's last place; the host: its own last place).
Run once: py.cmd tools/mini/patch59.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 59' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function toMenu(){if(sbBack())return;const wasSb=SBX&&NET.sbx&&NET.role;",
    "function toMenu(){if(sbBack())return;const wasSb=SBX&&NET.sbx&&NET.role&&!SB.shopBack;/* (patch 59: not for the shop) */")
rep("$('mpLeave').onclick=()=>{netLeave();netLobbyRender();};}}\n",
    "$('mpLeave').onclick=()=>{netLeave();netLobbyRender();};}\n"
    "  if(NET.sbx&&state==='menu'){const ch=box.querySelector('.mp-choices');if(ch&&!$('mpSb')){const b=document.createElement('button');b.id='mpSb';b.className='cta';b.type='button';b.textContent='Back to Sandbox';b.onclick=sbRoomBack;ch.prepend(b);}}/* (patch 59) */}\n"
    "/* (patch 59) from the room's screen back into the room's Sandbox: where the host is (a guest), or the host's own last place */\n"
    "function sbRoomBack(){if(!NET.role||!NET.sbx)return;let id=null;const hp=NET.role==='guest'&&SBN.peers.get(0);if(hp&&hp.reg)id=hp.reg;if(!id||!sbRegOf(id))id=SB.regId;if(!id||!sbRegOf(id))id=MAPS[mapIdx]&&MAPS[mapIdx].id;\n"
    "  if(!id||!sbRegOf(id))id='backyard';const mi=MAPS.findIndex(m=>m.id===id);if(mi<0)return;netHideLobby();try{if(garageOpen)closeGarage();}catch(e){}SB.shopBack=false;mode='sb';NET.fromNet=true;introSkip=true;menu.hidden=true;goRace(mi);}\n")
rep("closeGarage();if(NET.role==='guest'){netSendPick(true);goStep('home');netShowLobby();return;}if(typeof sbShopDone==='function'&&sbShopDone())return;goStep('track');};",
    "closeGarage();if(typeof sbShopDone==='function'&&sbShopDone())return;/* (patch 59: the shop's way out first, a room's guest too) */if(NET.role==='guest'){netSendPick(true);goStep('home');netShowLobby();return;}goStep('track');};")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 59 applied')
