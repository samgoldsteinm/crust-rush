#!/usr/bin/env python3
"""Put the Miniature Mayhem tracks and code (mini.js) into crust-rush.html, between their markers."""
import json, subprocess, sys
subprocess.check_call([sys.executable,'/home/claude/mini/t_bedroom.py'],stdout=subprocess.DEVNULL)
P='/home/claude/crust-rush.html'
s=open(P,encoding='utf-8').read()
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
ts=json.load(open('/home/claude/mini/tracks.json'))
between('/*MINI-MAPS-BEGIN*/','/*MINI-MAPS-END*/',''.join(',\n  '+js(t) for t in ts)+'\n')
code=open('/home/claude/mini/models.js',encoding='utf-8').read()+'\n'+open('/home/claude/mini/mini.js',encoding='utf-8').read()
assert all(ord(c)<0x10000 for c in code)
between('/*MINI-BEGIN*/','/*MINI-END*/','\n'+code)
open(P,'w',encoding='utf-8').write(s)
print('injected',len(ts),'tracks,',len(code),'chars')
