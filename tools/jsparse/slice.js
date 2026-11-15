// The web build's load slicer (docs/HANDOVER.md, "THE NO-STOP TUNNEL ON THE WEB"). Needs `npm install` in this folder once (acorn).
// usage: node slice.js game.js name1,name2,...   (rewrites game.js in place)
// Each named function declaration NAME becomes a generator NAMEG that yields between its statements (in blocks, if/else, loops, try, switch;
// never inside an inner function), and NAME itself stays a plain function that runs NAMEG to the end at once, so every other caller is
// unchanged. Inside a sliced function a call to another sliced function becomes (yield* OTHERG(...)), and a call whose callee is an
// expression, e.g. (a?f:g)(x), goes through __sl, which slices it when the function chosen is a sliced one. Nothing else changes: the
// statements run in the same order with the same values, so a place built in slices is the same place.
const fs=require('fs'),acorn=require('acorn'),walk=require('acorn-walk');
const file=process.argv[2],names=new Set(process.argv[3].split(',').filter(Boolean));
const src=fs.readFileSync(file,'utf8');
const ast=acorn.parse(src,{ecmaVersion:'latest'});
const F=new Map();
walk.full(ast,n=>{if(n.type==='FunctionDeclaration'&&n.id&&names.has(n.id.name)){if(F.has(n.id.name))throw new Error('two functions named '+n.id.name);F.set(n.id.name,n);}});
// also `const name=function(){...}` or `const name=(...)=>{...}` written inside a sliced function: the same, as NAMEG=function*(){...},NAME=(...a)=>__run(NAMEG(...a))
const X=[];{const top=new Set(F.values());walk.ancestor(ast,{VariableDeclarator(d,anc){if(d.id.type!=='Identifier'||!names.has(d.id.name)||!d.init)return;const f=d.init;
  if(!(f.type==='FunctionExpression'||(f.type==='ArrowFunctionExpression'&&f.body.type==='BlockStatement'))||f.async||f.generator)return;
  if(!anc.some(a=>top.has(a)))return;let bad=false;walk.ancestor(f.body,{ThisExpression(n,a2){if(f.type==='ArrowFunctionExpression'&&!a2.some(x=>x.type==='FunctionExpression'||x.type==='FunctionDeclaration'))bad=true;},Identifier(n,a2){if(n.name==='arguments'&&f.type==='ArrowFunctionExpression'&&!a2.some(x=>x.type==='FunctionExpression'||x.type==='FunctionDeclaration'))bad=true;}});
  if(bad)throw new Error(d.id.name+': an arrow that uses this or arguments');X.push(d);}});}
for(const n of names)if(!F.has(n)&&!X.some(d=>d.id.name===n))throw new Error('no function '+n);
if(/\b__sl\b|\b__run\b/.test(src))throw new Error('already sliced');
const fnodes=new Set([...F.values(),...X.map(d=>d.init)]),XN=new Set(X.map(d=>d.id.name)),E=[];let ny=0,nc=0;
const ed=(start,end,text,ord)=>E.push({start,end,text,ord});
// L: inside how many loops. Outside loops a yield goes before every statement; in a loop's body only one, at the start of each pass, and
// none in a loop inside a loop (a yield costs about as much as a small statement: 8 million of them made a whole load twice as slow)
const MAP=[];function Y(pos,txt){const id=MAP.length;MAP.push(pos);return txt.replace('yield;','yield '+id+';');}
let L=0;
function list(stmts){for(const s of stmts){if(L===0){ed(s.start,s.start,Y(s.start,'yield;'),2);ny++;}into(s);}}
function body(s,loop){if(loop&&L>0){/* a loop in a loop: a yield every 64 passes (a counter costs next to nothing; a yield does not) */if(s.type==='BlockStatement')ed(s.start+1,s.start+1,Y(s.start,'if(++__yc>63){__yc=0;yield;}'),2);else{ed(s.start,s.start,Y(s.start,'{if(++__yc>63){__yc=0;yield;}'),2);ed(s.end,s.end,'}',3);}ny++;L++;into(s);L--;return;}
  if(loop){if(L===0){if(s.type==='BlockStatement')ed(s.start+1,s.start+1,Y(s.start,'yield;'),2);else{ed(s.start,s.start,Y(s.start,'{yield;'),2);ed(s.end,s.end,'}',3);}ny++;}L++;into(s);L--;return;}
  if(s.type==='BlockStatement')list(s.body);else{/* a single statement as an if body: give it braces */if(L===0){ed(s.start,s.start,Y(s.start,'{yield;'),2);ed(s.end,s.end,'}',3);ny++;}into(s);}}
function into(s){switch(s.type){case'BlockStatement':list(s.body);break;case'IfStatement':body(s.consequent);if(s.alternate)body(s.alternate);break;
  case'ForStatement':case'ForOfStatement':case'ForInStatement':case'WhileStatement':case'DoWhileStatement':body(s.body,true);break;
  case'TryStatement':list(s.block.body);if(s.handler)list(s.handler.body.body);if(s.finalizer)list(s.finalizer.body);break;
  case'LabeledStatement':into(s.body);break;case'SwitchStatement':for(const c of s.cases)list(c.consequent);break;}}
for(const [name,f] of F){
  list(f.body.body);
  ed(f.start,f.id.end,'function '+name+'(...a){return __run('+name+'G.apply(this,a));}'+name+'.G='+name+'G;function* '+name+'G',0);}
for(const d of X){const f=d.init,name=d.id.name;list(f.body.body);ed(d.id.start,d.id.end,name+'G',0);
  if(f.type==='FunctionExpression')ed(f.start,f.start+8,'function*',0);else{/* (params)=>{ or x=>{ */const ps=f.params.length?src.slice(f.params[0].start,f.params[f.params.length-1].end):'';ed(f.start,f.body.start,'function*('+ps+')',0);}
  ed(d.end,d.end,','+name+'=(...a)=>__run('+name+'G(...a))',5);}
// calls
walk.ancestor(ast,{CallExpression(n,anc){let own=null;for(let i=anc.length-2;i>=0;i--){const a=anc[i];if(/Function/.test(a.type)){own=a;break;}}
  if(!own||!fnodes.has(own))return;const c=n.callee;
  if(c.type==='Identifier'&&(F.has(c.name)||XN.has(c.name))){ed(n.start,n.start,'(yield* ',1);ed(c.end,c.end,'G',1);ed(n.end,n.end,')',4);nc++;}
  else if(c.type==='ConditionalExpression'||c.type==='LogicalExpression'||c.type==='SequenceExpression'){ed(n.start,n.start,'(yield* __sl(',1);let p=c.end;while(/[)\s]/.test(src[p]))p++;if(src[p]!=='('||src[n.end-1]!==')')throw new Error('call shape at '+n.start);ed(p,p+1,',[',1);ed(n.end-1,n.end,']))',4);nc++;}}});
// a single-statement body made a block: '}' at its end must close after a ')' that ends there too
E.sort((a,b)=>b.start-a.start||a.ord-b.ord);
for(const r of E)if(r.end>r.start)for(const e of E)if(e!==r&&e.start>r.start&&e.start<r.end)throw new Error('an edit inside a rewritten call at '+r.start);
let out=src;for(const e of E)out=out.slice(0,e.start)+e.text+out.slice(e.end);
out='let __yc=0;function __run(g){let r;while(!(r=g.next()).done);return r.value;}function* __sl(f,a){return f&&f.G?yield* f.G(...a):f(...a);}\n'+out;
try{acorn.parse(out,{ecmaVersion:'latest'});}catch(e){const L=out.split('\n')[e.loc.line-1];console.error('slice: the result does not parse:',e.message,'\n',L.slice(Math.max(0,e.loc.column-300),e.loc.column+120));process.exit(2);}
fs.writeFileSync(file,out);
if(process.env.SLICE_MAP){/* for finding a slow slice: yield id -> the function and the code after it */const fnAt=p=>{for(const [n,f] of F)if(p>=f.start&&p<f.end)return n;return '?';};fs.writeFileSync(process.env.SLICE_MAP,JSON.stringify(MAP.map(p=>fnAt(p)+': '+src.slice(p,p+140).replace(/\s+/g,' '))));}
console.log('sliced',F.size+X.length,'functions, yields',ny,'calls',nc);
