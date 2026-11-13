# fifth engine patch (v155): room reflections on toy maps. Once the room is built it is photographed into a small cube
# map (toyRoomEnv, in mini.js) that replaces the map's designed environment. Run once: py.cmd tools\mini\patch5.py
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)
rep("function envProbe(){if(ENVP){try{ENVP.dispose();}catch(e){}ENVP=null;}",
    "function envProbe(){if(ENVP){try{ENVP.dispose();}catch(e){}ENVP=null;}if(TOYENV)return toyRoomEnv();/* a toy room photographs itself, on every quality setting */")
rep("function sunReset(){for(const o of SUNRCV)o.receiveShadow=false;SUNRCV=[];TOYSUN=null;sunBox();}",
    "function sunReset(){for(const o of SUNRCV)o.receiveShadow=false;SUNRCV=[];TOYSUN=null;TOYENV=null;sunBox();}")
open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
