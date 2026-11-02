// 把 offline.html 内联脚本降级到 Chrome 69 / Firefox 68 可解析的语法
const path=require('path');const L=path.join(__dirname,'..','node_modules')+path.sep;
const fs=require('fs'),esb=require(L+'esbuild'),acorn=require(L+'acorn');
const f=process.argv[2]; let s=fs.readFileSync(f,'utf8'); let n=0,bad=0;
s=s.replace(/<script>\n([\s\S]*?)\n<\/script>/g,(all,code)=>{
  let out=esb.transformSync(code,{loader:'js',target:['chrome69','firefox68'],charset:'utf8',legalComments:'inline'}).code;
  try{acorn.parse(out,{ecmaVersion:2019,sourceType:'script'})}catch(e){bad++;console.error('ES2019 parse fail',e.message)}
  n++; return '<script>\n'+out.replace(/<\/script/gi,'<\\/script')+'\n</script>';
});
fs.writeFileSync(f,s); console.log('scripts',n,'es2019-fail',bad);
