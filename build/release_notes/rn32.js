const {P,H,TBL,build,Packer,Paragraph,TextRun,AlignmentType,rf,CNH,CN,rich}=require('./lib.js');
const body=[]; const add=(...a)=>a.forEach(x=>Array.isArray(x)?body.push(...x):body.push(x));
const LI=(t)=>new Paragraph({children:rich(t,{}),numbering:{reference:'bul',level:0},spacing:{line:330,lineRule:'auto',after:40},alignment:AlignmentType.LEFT});
const C=(t,size,font,bold,after)=>new Paragraph({alignment:AlignmentType.CENTER,indent:{firstLine:0},spacing:{after:after||120},children:[new TextRun({text:t,size,bold:!!bold,font:rf(font)})]});
const cover=[new Paragraph({spacing:{before:3200},children:[]}),C('经纬织图',52,CNH,true,200),C('V3.2　发布说明',36,CNH,true,1600),C(require('./lib.js').BRAND.org,30,CN,false,120),C('2026 年 10 月 18 日',28,CN,false,120)];
add(P('**v3.2 新增“单侧圆角矩形”图形：一侧两角为圆角、另一侧为直角，分左圆、右圆两种；导出 PPT、Visio、draw.io 均保持原样，并可原样导回。本版同时包含 v3.1.1 的银河麒麟（飞腾）环境适配。**'));
add(H('一、新增图形',1));
add(TBL('单侧圆角矩形',['名称','形状','用法'],[
 ['左圆角矩形','左侧两角圆角，右侧两角直角','左侧图形库“基础形状”中拖入；或选中已有框，在属性面板“形状”中切换'],
 ['右圆角矩形','右侧两角圆角，左侧两角直角','同上'],
],[1800,2800,4000]));
['**圆角大小**：与“圆角矩形”一致（最大 10 像素，框较小时按高度的三分之一取值），同一张图中两类圆角协调统一。','**文字与图标**：文字区、图标位置与矩形一致；支持状态着色（已建、本期新增、重点建设）、连线从边中点出入、一键美化。'].forEach(t=>add(LI(t)));
add(H('二、导出与导入',1));
add(TBL('各格式下的表现',['格式','导出','导回本软件'],[
 ['PowerPoint','自由曲线图形，文字在形状内，可在 PPT 中编辑顶点','识别为对应的单侧圆角矩形'],
 ['Visio','几何轮廓逐点还原','识别为对应的单侧圆角矩形'],
 ['draw.io','可配置矩形（左上／左下或右上／右下设为圆角），在 draw.io 中可继续调整','识别为对应的单侧圆角矩形'],
 ['PNG／SVG','与画布一致','—'],
],[1600,4200,2800]));
add(P('从他人 PPT 导入时，旋转 90°／270° 的“同侧圆角矩形”也会识别为单侧圆角矩形。'));
add(H('三、国产环境适配（v3.1.1 起）',1));
['**运行环境**：银河麒麟桌面操作系统（国防版）V10、飞腾 D2000、UKUI；Windows 7～11。','**浏览器要求**：Chromium 内核 69 以上（奇安信可信浏览器、360 安全浏览器信创版等）或 Firefox 68 以上；版本过低时页面顶部给出提示。'].forEach(t=>add(LI(t)));
(async()=>{require('fs').writeFileSync('ReleaseNotes_v3.2.docx',await Packer.toBuffer(build({title:'经纬织图 V3.2 发布说明',header:'经纬织图　V3.2 发布说明',cover,body})));console.log('ok')})();
