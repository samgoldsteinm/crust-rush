#!/bin/bash
# build the web game and make a hooked test copy served on port 8771
set -e
SP=/tmp/claude-0/-home-claude/009aa3b6-e96f-505b-b230-9e07dd3a3292/scratchpad
cd /home/claude && node -e "const s=require('fs').readFileSync('crust-rush.html','utf8');for(const x of s.matchAll(/<script(?![^>]*src)[^>]*>([\\s\\S]*?)<\\/script>/g)){new Function(x[1]);}" && python3 /tmp/claude-0/gh/build_gh.py crust-rush-v155 > /dev/null
rm -rf $SP/webcopy6 && cp -r /home/claude/crust-rush-app $SP/webcopy6 && rm -rf $SP/webcopy6/.git
python3 - <<'PY'
import glob
SP='/tmp/claude-0/-home-claude/009aa3b6-e96f-505b-b230-9e07dd3a3292/scratchpad'
f=glob.glob(SP+'/webcopy6/js/game.*.js')[0]
s=open(f,encoding='utf-8').read()
i=s.rindex('})();')
s=s[:i]+'window.__ev=(x)=>eval(x);'+s[i:]
open(f,'w',encoding='utf-8').write(s)
PY
pgrep -f "http.server 8771" > /dev/null || (cd $SP && nohup python3 -m http.server 8771 > /dev/null 2>&1 &)
echo built
