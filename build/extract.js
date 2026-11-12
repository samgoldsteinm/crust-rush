const fs=require('fs');const s=fs.readFileSync(process.argv[2]||'D:/crust-rush/source/crust-rush.html','utf8');
function lit(name){const k='const '+name+'=';const i=s.indexOf(k)+k.length;let d=0,j=i,q=null;
 for(;j<s.length;j++){const c=s[j];if(q){if(c==='\\'){j++;continue;}if(c===q)q=null;continue;}
  if(c==='"'||c==="'"||c==='`'){q=c;continue;}if(c==='{')d++;else if(c==='}'){d--;if(d===0){j++;break;}}}
 return {start:i,end:j,val:eval('('+s.slice(i,j)+')')};}
const out={};for(const n of ['CAR_PACKS','PROP_PACKS','PROP_TEX','MAP_SHOTS']){const r=lit(n);out[n]={start:r.start,end:r.end};fs.writeFileSync(n+'.json',JSON.stringify(r.val));}
fs.writeFileSync('spans.json',JSON.stringify(out));console.log(out);
