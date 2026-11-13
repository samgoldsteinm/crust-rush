#!/usr/bin/env python3
"""Put the Miniature Mayhem tracks and code (mini.js) into crust-rush.html, between their markers."""
import json, subprocess, sys
for t in ('t_bedroom.py','t_kitchen.py','t_garage.py'):   # each writes its own entry into tracks.json (the bedroom first: it starts the list)
    subprocess.check_call([sys.executable,'D:/crust-rush/source/tools/mini/'+t],stdout=subprocess.DEVNULL)
P='D:/crust-rush/source/crust-rush.html'
s=open(P,encoding='utf-8',newline='').read()
def between(a,b,new):
    global s
    i=s.index(a)+len(a); e=s.index(b,i); s=s[:i]+new+s[e:]
def js(v):
    if isinstance(v,str): return "'"+v.replace("\\","\\\\").replace("'","\\'")+"'"
    if isinstance(v,bool): return 'true' if v else 'false'
    if isinstance(v,(int,float)): return ('%g'%v) if isinstance(v,float) else str(v)
    if isinstance(v,list): return '['+','.join(js(x) for x in v)+']'
    if isinstance(v,dict): return '{'+','.join(k+':'+js(x) for k,x in v.items())+'}'
    raise TypeError(v)
ts=json.load(open('D:/crust-rush/source/tools/mini/tracks.json'))
between('/*MINI-MAPS-BEGIN*/','/*MINI-MAPS-END*/',''.join(',\n  '+js(t) for t in ts)+'\n')
code=open('D:/crust-rush/source/tools/mini/models.js',encoding='utf-8',newline='').read()+'\n'+open('D:/crust-rush/source/tools/mini/mini.js',encoding='utf-8',newline='').read()
assert all(ord(c)<0x10000 for c in code)
between('/*MINI-BEGIN*/','/*MINI-END*/','\n'+code)
open(P,'w',encoding='utf-8',newline='').write(s)
print('injected',len(ts),'tracks,',len(code),'chars')
