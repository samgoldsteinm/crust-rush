#!/usr/bin/env python3
"""Put track pictures into the web game (MAP_SHOTS) and the PC build (assets/shots).
usage: embed_shots.py <folder with <id>-<h|m|a>.jpg> [infos.json]   (infos: {id: {len, glide, loop, ramps, shorts, tunnel, surf}})"""
import base64, json, os, re, shutil, sys
P='D:/crust-rush/source/crust-rush.html'; PC='D:/crust-rush/godot/assets/shots'
src=sys.argv[1]; infos=json.load(open(sys.argv[2])) if len(sys.argv)>2 else {}
sys.path.insert(0,'D:/crust-rush/source/tools'); import tables
D=tables.load('MAP_SHOTS')   # (the table is files under source/data/shots: tools/tables.py)
n=0
for f in sorted(os.listdir(src)):
    m=re.match(r'^([a-z]+)-([hma])\.jpg$',f)
    if not m: continue
    mid,k=m.groups(); b=open(os.path.join(src,f),'rb').read()
    D.setdefault(mid,{})[k]=base64.b64encode(b).decode(); shutil.copy(os.path.join(src,f),os.path.join(PC,f)); n+=1
for mid,inf in infos.items():
    D.setdefault(mid,{})['i']=inf
tables.save('MAP_SHOTS',D)
print('embedded',n,'pictures; maps:',len(D))
