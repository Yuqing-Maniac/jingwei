const docx=require('docx');
const {Document,Packer,Paragraph,TextRun,HeadingLevel,AlignmentType,Table,TableRow,TableCell,
  WidthType,ShadingType,BorderStyle,VerticalAlign,ImageRun,SimpleField,TableOfContents,
  Header,Footer,PageNumber,PageBreak,LevelFormat,convertMillimetersToTwip}=docx;
const fs=require('fs');
const BRAND=require('../brand.js');   // 机构标识：brand.local.json（不入库）> brand.example.json
const sizeOf=(p)=>{const b=fs.readFileSync(p);
  if(b[0]===0x89&&b[1]===0x50) return {w:b.readUInt32BE(16),h:b.readUInt32BE(20)};
  return {w:1600,h:1000};};

const CN='仿宋', CNK='楷体', CNH='黑体', EN='Times New Roman';
const SZ={body:24, tbl:21, tbls:18, cap:21, h1:32, h2:28, h3:24, h4:24, cover:44, cover2:30};
function rf(ea){ return {ascii:EN,hAnsi:EN,cs:EN,eastAsia:ea,hint:'eastAsia'}; }

/* 富文本：**加粗**；（括号内容）自动转楷体 */
function rich(t,o){
  o=o||{};
  const base=o.font||CN, size=o.size||SZ.body, color=o.color||'000000';
  const out=[];
  String(t).split('**').forEach((seg,bi)=>{
    if(seg==='') return;
    const bold=(bi%2===1)||!!o.bold;
    if(o.noKai){ out.push(new TextRun({text:seg,bold,size,color,font:rf(base)})); return; }
    const re=/（[^（）]*）/g; let last=0,m;
    while((m=re.exec(seg))!==null){
      if(m.index>last) out.push(new TextRun({text:seg.slice(last,m.index),bold,size,color,font:rf(base)}));
      out.push(new TextRun({text:m[0],bold,size,color,font:rf(CNK)}));   // 括号转楷体
      last=m.index+m[0].length;
    }
    if(last<seg.length) out.push(new TextRun({text:seg.slice(last),bold,size,color,font:rf(base)}));
  });
  return out;
}

function P(t,o){
  o=o||{};
  return new Paragraph({children:rich(t,o),
    alignment:o.align||AlignmentType.JUSTIFIED,
    spacing:{line:o.line||330,lineRule:'auto',before:o.before||0,after:o.after||60},
    indent:o.indent!==undefined?o.indent:{firstLine:480},   // 首行缩进二字
    keepNext:!!o.keepNext});
}

function LI(t,lvl){
  return new Paragraph({children:rich(t,{}),
    numbering:{reference:'bul',level:lvl||0},
    spacing:{line:330,lineRule:'auto',after:40},
    alignment:AlignmentType.JUSTIFIED});
}

function H(t,lv){
  const map={1:HeadingLevel.HEADING_1,2:HeadingLevel.HEADING_2,3:HeadingLevel.HEADING_3,4:HeadingLevel.HEADING_4};
  const sz={1:SZ.h1,2:SZ.h2,3:SZ.h3,4:SZ.h4}[lv];
  const fnt={1:CNH,2:CNH,3:CNH,4:CNK}[lv];
  return new Paragraph({heading:map[lv],
    children:[new TextRun({text:t,bold:true,size:sz,font:rf(fnt),color:'000000'})],
    spacing:{before:lv===1?300:200,after:lv===1?160:110,line:330,lineRule:'auto'},
    indent:{firstLine:0}, keepNext:true});
}

/* 图：图在上，题注在下，SEQ 自动编号 */
function FIG(path,cap,maxW){
  const d=sizeOf(path), W=maxW||420, H=Math.round(W*d.h/d.w);
  return [
    new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:140,after:40},
      indent:{firstLine:0}, keepNext:true,
      children:[new ImageRun({type:'png',data:fs.readFileSync(path),
                              transformation:{width:W,height:H}})]}),
    new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:160},indent:{firstLine:0},
      children:[
        new TextRun({text:'图 ',size:SZ.cap,font:rf(CNH),bold:true}),
        new SimpleField('SEQ 图 \\* ARABIC'),
        new TextRun({text:'　'+cap,size:SZ.cap,font:rf(CNH),bold:true})]})
  ];
}

/* 表：题注在上，表在下，SEQ 自动编号 */
function TCAP(cap){
  return new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:160,after:50},
    indent:{firstLine:0}, keepNext:true,
    children:[
      new TextRun({text:'表 ',size:SZ.cap,font:rf(CNH),bold:true}),
      new SimpleField('SEQ 表 \\* ARABIC'),
      new TextRun({text:'　'+cap,size:SZ.cap,font:rf(CNH),bold:true})]});
}

function cell(t,o){
  o=o||{};
  return new TableCell({
    width:{size:o.w,type:WidthType.DXA},
    shading:o.head?{type:ShadingType.CLEAR,fill:'DCE6EC',color:'auto'}:
           (o.fill?{type:ShadingType.CLEAR,fill:o.fill,color:'auto'}:undefined),
    verticalAlign:VerticalAlign.CENTER,
    margins:{top:40,bottom:40,left:70,right:70},
    columnSpan:o.span,
    children:String(t).split('\n').map(ln=>new Paragraph({
      alignment:o.align||(o.head?AlignmentType.CENTER:AlignmentType.LEFT),
      spacing:{line:270,lineRule:'auto',before:0,after:0},indent:{firstLine:0},
      children:rich(ln,{size:o.small?SZ.tbls:SZ.tbl,bold:o.head,font:o.head?CNH:CN})}))});
}

function TBL(cap,head,rows,cw,opt){
  opt=opt||{};
  const total=cw.reduce((a,b)=>a+b,0);
  const bd={style:BorderStyle.SINGLE,size:4,color:'8FA4B2'};
  const tr=[];
  if(head) tr.push(new TableRow({tableHeader:true,
    children:head.map((h,i)=>cell(h,{w:cw[i],head:true,small:opt.small}))}));
  rows.forEach(r=>tr.push(new TableRow({children:r.map((c,i)=>{
    if(c&&typeof c==='object') return cell(c.t,Object.assign({w:cw[i],small:opt.small},c));
    return cell(c,{w:cw[i],small:opt.small,
      align:(opt.center&&opt.center.indexOf(i)>=0)?AlignmentType.CENTER:undefined});
  })})));
  const t=new Table({columnWidths:cw,width:{size:total,type:WidthType.DXA},
    borders:{top:bd,bottom:bd,left:bd,right:bd,insideHorizontal:bd,insideVertical:bd},
    rows:tr});
  return cap?[TCAP(cap),t,P('',{after:100,indent:{firstLine:0}})]
            :[t,P('',{after:100,indent:{firstLine:0}})];
}

function build(o){
  const secProps={page:{
    size:{width:convertMillimetersToTwip(210),height:convertMillimetersToTwip(297)},
    margin:{top:convertMillimetersToTwip(28),bottom:convertMillimetersToTwip(26),
            left:convertMillimetersToTwip(28),right:convertMillimetersToTwip(24)}}};
  const hdr=new Header({children:[new Paragraph({alignment:AlignmentType.CENTER,indent:{firstLine:0},
    border:{bottom:{style:BorderStyle.SINGLE,size:6,color:'808080',space:2}},
    children:[new TextRun({text:o.header,size:18,font:rf(CNK),color:'404040'})]})]});
  const ftr=new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,indent:{firstLine:0},
    children:[new TextRun({children:['— ',PageNumber.CURRENT,' —'],size:20,font:rf(CN)})]})]});
  return new Document({
    creator:o.creator||BRAND.org, title:o.title, description:o.desc||'',
    numbering:{config:[{reference:'bul',levels:[
      {level:0,format:LevelFormat.BULLET,text:'●',alignment:AlignmentType.LEFT,
       style:{paragraph:{indent:{left:960,hanging:240}},run:{size:18}}},
      {level:1,format:LevelFormat.BULLET,text:'○',alignment:AlignmentType.LEFT,
       style:{paragraph:{indent:{left:1440,hanging:240}},run:{size:18}}}]}]},
    styles:{default:{document:{run:{font:rf(CN),size:SZ.body,color:'000000'},
      paragraph:{spacing:{line:330,lineRule:'auto'}}}},
      paragraphStyles:[1,2,3,4].map(i=>({
        id:'Heading'+i, name:'Heading '+i, basedOn:'Normal', next:'Normal', quickFormat:true,
        run:{size:SZ['h'+i],bold:true,font:rf(i===4?CNK:CNH),color:'000000'},
        paragraph:{outlineLevel:i-1}}))},
    sections:[
      {properties:secProps,children:o.cover},
      {properties:Object.assign({},secProps),headers:{default:hdr},footers:{default:ftr},
       children:o.body}]});
}

module.exports={BRAND,docx,Paragraph,TextRun,AlignmentType,PageBreak,TableOfContents,Packer,
  P,LI,H,FIG,TBL,TCAP,cell,rich,build,SZ,CN,CNK,CNH,EN,rf};
