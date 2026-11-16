"""Patch 47d (web v209): the controller's cursor clicks the Records rows, and its speed is a setting.
The owner: "the onscreen mouse on pc cant click the tracks to see records it doesnt register the click and i have to use my pc mouse.
also it moves too fast lets add a cursor speed in settings for both mobile and pc".
- The Records rows that open a world board (patch 44, li.lb-open) only had an onclick; the controller's A clicks what matches PAD_CLICK
  (buttons, links, .mapc ...), which they did not. They are in PAD_CLICK now. Anything new made clickable with a bare onclick must be
  added there too (or be a button).
- Settings > Controller cursor speed (CFG.curs, 25 to 200 %, 70 if never set: it was too fast at 100). It scales the stick and the
  D-pad (PAD_MOB, still slower again on a phone); the right stick's scrolling is unchanged.
Run once: py.cmd tools/mini/patch47d.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 47d' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("""const PAD_CLICK='button,a[href],input,select,label,summary,[tabindex]:not([tabindex="-1"]),.mapc,.cupc,[role=button]';""",
    """const PAD_CLICK='button,a[href],input,select,label,summary,[tabindex]:not([tabindex="-1"]),.mapc,.cupc,[role=button],.lb-open';/* (patch 47d: the Records rows) */""")
rep("const PAD_MOB=()=>typeof COARSE!=='undefined'&&COARSE?.55:1,",
    "const PAD_MOB=()=>(typeof COARSE!=='undefined'&&COARSE?.55:1)*((typeof CFG!=='undefined'&&CFG.curs)||70)/100,/* (patch 47d: the cursor speed setting) */")
rep("""<input type="range" id="camdR" min="75" max="150" step="5" aria-label="Camera distance"><output id="camdO"></output></div></div>""",
    """<input type="range" id="camdR" min="75" max="150" step="5" aria-label="Camera distance"><output id="camdO"></output></div></div>"""
    """       <div class="set-row"><div class="set-t"><b>Controller cursor speed</b><small>How fast the on-screen cursor moves in menus when you use a controller.</small></div>"""
    """<div class="vol"><input type="range" id="cursR" min="25" max="200" step="5" aria-label="Controller cursor speed"><output id="cursO"></output></div></div>""")
rep("$('camdR').value=CFG.camd||100;$('camdO').textContent=(CFG.camd||100)+'%';",
    "$('camdR').value=CFG.camd||100;$('camdO').textContent=(CFG.camd||100)+'%';$('cursR').value=CFG.curs||70;$('cursO').textContent=(CFG.curs||70)+'%';")
rep("$('camdR').oninput=e=>{CFG.camd=+e.target.value;$('camdO').textContent=CFG.camd+'%';saveCfg();};",
    "$('camdR').oninput=e=>{CFG.camd=+e.target.value;$('camdO').textContent=CFG.camd+'%';saveCfg();};$('cursR').oninput=e=>{CFG.curs=+e.target.value;$('cursO').textContent=CFG.curs+'%';saveCfg();};")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 47d applied')
