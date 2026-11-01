const {P,H,TBL,build,Packer,Paragraph,TextRun,AlignmentType,rf,CNH,CN,rich}=require('./lib.js');
const body=[]; const add=(...a)=>a.forEach(x=>Array.isArray(x)?body.push(...x):body.push(x));
const LI=(t)=>new Paragraph({children:rich(t,{}),numbering:{reference:'bul',level:0},spacing:{line:330,lineRule:'auto',after:40},alignment:AlignmentType.LEFT});
const C=(t,size,font,bold,after)=>new Paragraph({alignment:AlignmentType.CENTER,indent:{firstLine:0},spacing:{after:after||120},children:[new TextRun({text:t,size,bold:!!bold,font:rf(font)})]});
const cover=[new Paragraph({spacing:{before:3200},children:[]}),C('经纬体系绘图',52,CNH,true,200),C('V3.0　发布说明',36,CNH,true,1600),C(require('./lib.js').BRAND.org,30,CN,false,120),C('2026 年 10 月 18 日',28,CN,false,120)];
add(P('**v3.0 起软件更名为“经纬体系绘图”，取“纵横经纬、体系成图”之意；本版重做连线的出入点与绕行规则：连线一律从框边中点出入，同边多条线以中点为中心对称排布；绕行时拐弯最少、自动选择出入边。**'));
add(H('一、软件更名',1));
['**新名称**：经纬体系绘图（英文 JingWei），程序文件为“JingWei_v3.0.html”。','**兼容**：以前保存的工程文件（.hongtu.json 等）可直接打开；新保存的工程文件扩展名为 .jingwei.json。各项本机设置（大模型接口、转换选项等）保留。'].forEach(t=>add(LI(t)));
add(H('二、连线出入点',1));
add(P('**每条连线从框边的中点出入；同一条边上有多条连线时，各线端点以边中点为中心对称排布、间距一致。**'));
['**直线优先**：两框中点对齐时直连；相差在 12 像素以内且不越出边界时取直，避免小折线。','**一对多**：一端是多条线的分布端、另一端只有一条线时，单线端随之对正，走直线。','**嵌套不交叉**：同一边上的端口顺序按走向自动调换，绕行的 U 形线外圈用外侧端口，相互不交叉。'].forEach(t=>add(LI(t)));
add(H('三、一键美化（方框＋连线的流程图）',1));
['**上下对正**：跨行相连的两个框，列位置接近时下方的框对正到上方框的中线下，连线成为从边中点出发的直线；挡路的框顺势让位。','**等间距**：夹在两个对正框之间的其他框等间距分布。','**统一尺寸与行列对齐**：框按文字定统一尺寸、不放大，行与列中线取齐（v2.8 起）。'].forEach(t=>add(LI(t)));
add(H('四、连线避障',1));
add(TBL('避障规则',['规则','说明'],[
 ['拐弯最少','每拐一次弯计较大的代价，优先少拐弯、长直线的走法'],
 ['自选出入边','绕行时出入边不限于相对的两边，可从上、下、左、右任一边中点出入；如“指挥中心→无人机”中间隔着“中继站”时，从两框上边出入，越过中间框'],
 ['分走两侧','同一对框之间的多条绕行线，优先分走上下两侧；同侧时错开 8 像素平行'],
 ['标签不重叠','连线标签依次落位，避开框和已放的标签'],
 ['图面完整','绕到图外侧的连线及标签计入图面范围，导出不裁切'],
],[1800,6800]));
add(H('五、其他',1));
['**拖动吸附**（v2.8 起）：对齐其他图形的边与中线、画布中轴、容器中线，提示等间距；按住 Alt 临时关闭。','**格式转换**（v2.7.1 起）：Visio 转 PowerPoint 逐形状原样还原字体字号。','**运行环境**：Windows 7～11、麒麟（x86／飞腾）；建议使用 Chrome、Edge 或其他 Chromium 内核浏览器。'].forEach(t=>add(LI(t)));
(async()=>{require('fs').writeFileSync('ReleaseNotes_v3.0.docx',await Packer.toBuffer(build({title:'经纬体系绘图 V3.0 发布说明',header:'经纬体系绘图　V3.0 发布说明',cover,body})));console.log('ok')})();
