const {P,H,TBL,build,Packer,Paragraph,TextRun,AlignmentType,rf,CNH,CN,rich}=require('./lib.js');
const body=[]; const add=(...a)=>a.forEach(x=>Array.isArray(x)?body.push(...x):body.push(x));
const LI=(t)=>new Paragraph({children:rich(t,{}),numbering:{reference:'bul',level:0},spacing:{line:330,lineRule:'auto',after:40},alignment:AlignmentType.LEFT});
const C=(t,size,font,bold,after)=>new Paragraph({alignment:AlignmentType.CENTER,indent:{firstLine:0},spacing:{after:after||120},children:[new TextRun({text:t,size,bold:!!bold,font:rf(font)})]});
const cover=[new Paragraph({spacing:{before:3200},children:[]}),C('经纬织图',52,CNH,true,200),C('V3.2.1　发布说明',36,CNH,true,1600),C(require('./lib.js').BRAND.org,30,CN,false,120),C('2026 年 10 月 18 日',28,CN,false,120)];
add(P('**v3.2.1 为质量修订版：对全部 20 套模板、7 种导出格式、37 个公开 Visio 样例及全部界面操作进行系统排查，修复 11 项问题；银河麒麟（飞腾）环境已实测可用。**'));
add(H('一、排查范围',1));
['**模板**：20 套模板分别按标准、紧凑、报告版心三种排版运行一键美化与减少交叉。','**导出与导回**：PNG、透明 PNG、报告插图、PPT、Visio、draw.io、SVG 及规范表格（xlsx）；PPT、Visio、draw.io 导出后再导回比对。','**导入**：37 个公开 Visio 样例逐个导入并美化。','**界面**：全部图形、拖动缩放、撤销重做、复制粘贴、属性面板、多页面、保存重开、文字成图、参照生成（离线模式）及 F1 所列全部快捷键。'].forEach(t=>add(LI(t)));
add(H('二、修复内容',1));
add(TBL('修复清单',['序号','问题','修复'],[
['1','报告版心排导入的图，字号仅约 6.5 磅','超宽元素按版心宽重排或整体收进版心，字号恢复到约 10.5 磅'],
['2','PPT 中圆角矩形的圆角明显小于画布','圆角半径与画布一致，Visio 导出同步'],
['3','一层内图形过多时一键美化报错','放不下时自动折成多行网格'],
['4','连线接菱形、椭圆、云等图形时线头悬空','端点贴合图形轮廓'],
['5','相邻框间的连线标签压在框上','自动放宽间距，标签不再压框'],
['6','折行后标点落在行首','增加行首标点禁则'],
['7','draw.io 导回时文字带编号前缀','导回时去除编号前缀'],
['8','Visio 导回时宽矮说明框被识别为菱形','横纵向分别判断'],
['9','PPT、Visio 导回时连线标签变成方框、短连线丢失','标签归还对应连线，连线完整保留'],
['10','打开损坏文件时提示英文','改为中文说明'],
['11','子容器编号牌压住标题','标题让开编号牌'],
],[700,3900,4000]));
add(H('三、已知限制',1));
['**报告版心下 4 列以上的宽图**：受版心宽度约束，个别连线标签仍较拥挤，可改用横版或标准排版。','**标题栏**：导出到 PPT、Visio 后为普通单元格，导回本软件时不还原为标题栏。'].forEach(t=>add(LI(t)));
add(H('四、运行环境',1));
['**系统**：Windows 7～11；银河麒麟桌面操作系统（国防版）V10、飞腾 D2000（已实测）。','**浏览器**：Chromium 内核 69 以上或 Firefox 68 以上。'].forEach(t=>add(LI(t)));
(async()=>{require('fs').writeFileSync('ReleaseNotes_v3.2.1.docx',await Packer.toBuffer(build({title:'经纬织图 V3.2.1 发布说明',header:'经纬织图　V3.2.1 发布说明',cover,body})));console.log('ok')})();
