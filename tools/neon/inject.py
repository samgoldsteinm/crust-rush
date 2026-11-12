#!/usr/bin/env python3
"""Put the neon tracks (gen.py) and the neon code (neon.js) into crust-rush.html, between their markers."""
import json, re, subprocess, sys
sys.path.insert(0,'/home/claude/neon')
subprocess.check_call([sys.executable,'/home/claude/neon/gen.py','js'])
P='/home/claude/crust-rush.html'
s=open(P,encoding='utf-8').read()
def between(a,b,new):
    global s
    i=s.index(a)+len(a); e=s.index(b,i)
    s=s[:i]+new+s[e:]
def js(v):
    if isinstance(v,str): return "'"+v.replace("\\","\\\\").replace("'","\\'")+"'"
    if isinstance(v,bool): return 'true' if v else 'false'
    if isinstance(v,(int,float)): return ('%g'%v) if isinstance(v,float) else str(v)
    if isinstance(v,list): return '['+','.join(js(x) for x in v)+']'
    if isinstance(v,dict): return '{'+','.join(k+':'+js(x) for k,x in v.items())+'}'
    raise TypeError(v)
ts=json.load(open('/home/claude/neon/tracks.json'))
out=''
for t in ts:
    out+=',\n  '+js(t)
between('/*NEON-MAPS-BEGIN*/','/*NEON-MAPS-END*/',out+'\n')
code=open('/home/claude/neon/neon.js',encoding='utf-8').read()
assert all(ord(c)<0x10000 for c in code)
between('/*NEON-BEGIN*/','/*NEON-END*/','\n'+code)
open(P,'w',encoding='utf-8').write(s)
print('injected',len(ts),'tracks,',len(code),'chars of code')
