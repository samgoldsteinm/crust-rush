# thirteenth patch (v167): the garage shows stats the way the PC version does (the user's request).
# - A vehicle's card shows its own stats as plain values out of 12 ("SPD 7"), no plus or minus. A bike's built-in wheels count
#   as part of the vehicle. Wheel and glider cards keep their plus and minus chips: they are changes to the vehicle.
# - The stats panel: the vehicle's own bars in orange; what the wheels and glider add in green, what they take away in red;
#   the number beside each bar is that change (blank when they change nothing). Same scale as the PC (6 + soft x 1.5, 0..12).
# - Pointing at a part previews the build it would make (the PC highlights the same way).
# Display only: statMods, which the race uses, is untouched.
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)


rep("function partChips(st){",
    """/* the 0..12 bars of a build (PC KartBuilder._bars): all of it, or the vehicle on its own (the body, and a bike's built-in wheels) */
function statBarsOf(b,all){const o=[0,0,0,0,0],bd=BODIES[b.b],bike=!!(bd.bike&&bd.bw);[bd,wheelOf(b),GLIDERS[b.g]].forEach((p,k)=>{if(!all&&(k===2||(k===1&&!bike)))return;for(let i=0;i<5;i++)o[i]+=p.st[i]*STAT_W[k];});return o.map(r=>clamp(Math.round(STAT_MID+statSoft(r)*1.5),0,STAT_BARS));}
/* a vehicle's own stats as plain values, for its card: they are what it is, not a change to anything */
function valueChips(bars){return bars.map((v,i)=>'<em class="nt">'+STAT_SHORT[i]+' '+v+'</em>').join('');}
/* the stats panel for a build: the vehicle's bars, what the wheels and glider add (green) and take away (red), and that change as a number */
function showStats(b){const base=statBarsOf(b,false),tot=statBarsOf(b,true);$('gStats').querySelectorAll('.st-row').forEach((r,i)=>{const n=base[i],t=tot[i];
    r.querySelectorAll('i').forEach((c,j)=>{c.classList.toggle('on',j<Math.min(n,t));c.classList.toggle('gain',j>=n&&j<t);c.classList.toggle('loss',j>=t&&j<n);c.classList.toggle('mid',j===STAT_MID-1);});
    const d=r.querySelector('.st-d'),ch=t-n;d.textContent=ch?(ch>0?'+':'\\u2212')+Math.abs(ch):'';d.className='st-d'+(ch>0?' up':ch<0?' dn':'');});}
function partChips(st){""")
rep("""b.innerHTML='<b>'+p.name+'</b><span class="pd">'+p.desc+'</span><span class="chips">'+partChips(p.st)+'</span>';b.onclick=()=>{playerBuild[key]=i;""",
    """b.innerHTML='<b>'+p.name+'</b><span class="pd">'+p.desc+'</span><span class="chips">'+(key==='b'?valueChips(statBarsOf({b:i,w:0,g:0},false)):partChips(p.st))+'</span>';
    /* pointing at a part shows the build it would make */b.onpointerenter=()=>showStats(Object.assign({},playerBuild,{[key]:i}));b.onpointerleave=()=>showStats(playerBuild);b.onclick=()=>{playerBuild[key]=i;""")
rep("""  const st=statRaw(playerBuild);
  $('gStats').querySelectorAll('.st-row').forEach((r,i)=>{const sv=statSoft(st[i]),v=clamp(Math.round(STAT_MID+sv*1.4),1,STAT_BARS);r.querySelectorAll('i').forEach((c,j)=>{c.classList.toggle('on',j<v);c.classList.toggle('mid',j===STAT_MID-1);});
    const d=r.querySelector('.st-d'),n=v-STAT_MID;d.textContent=n?(n>0?'+':'\u2212')+Math.abs(n):'0';d.className='st-d'+(n>0?' up':n<0?' dn':'');});
""", """  showStats(playerBuild);
""")
rep(""".st-bar i.on{background:linear-gradient(90deg,#f7c948,#ff8a1f)}.st-bar i.mid{""", """.st-bar i.on{background:linear-gradient(90deg,#f7c948,#ff8a1f)}.st-bar i.gain{background:#6fe06a}.st-bar i.loss{background:rgba(255,107,84,.85)}.st-bar i.mid{""")
rep(""".g-stats.off{opacity:.55}.g-stats.off .st-bar i.on{background:rgba(255,244,220,.35)}""", """.g-stats.off{opacity:.55}.g-stats.off .st-bar i.on,.g-stats.off .st-bar i.gain,.g-stats.off .st-bar i.loss{background:rgba(255,244,220,.35)}""")
open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
