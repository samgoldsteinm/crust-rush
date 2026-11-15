// usage: node span.js file.html fnName -> "start end" offsets (in the file) of the function declaration
const fs=require('fs'),acorn=require('acorn'),walk=require('acorn-walk');
const html=fs.readFileSync(process.argv[2],'utf8'),fn=process.argv[3];
const re=/<script>([\s\S]*?)<\/script>/g;let m;while((m=re.exec(html))){if(!m[1].includes('function '+fn+'('))continue;const off=m.index+8,ast=acorn.parse(m[1],{ecmaVersion:'latest'});
  walk.full(ast,n=>{if(n.type==='FunctionDeclaration'&&n.id&&n.id.name===fn)console.log(off+n.start,off+n.end);});}
