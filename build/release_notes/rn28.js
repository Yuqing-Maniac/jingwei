const {P,H,TBL,build,Packer,Paragraph,TextRun,AlignmentType,rf,CNH,CN,rich}=require('./lib.js');
const body=[]; const add=(...a)=>a.forEach(x=>Array.isArray(x)?body.push(...x):body.push(x));
const LI=(t)=>new Paragraph({children:rich(t,{}),numbering:{reference:'bul',level:0},spacing:{line:330,lineRule:'auto',after:40},alignment:AlignmentType.LEFT});
const C=(t,size,font,bold,after)=>new Paragraph({alignment:AlignmentType.CENTER,indent:{firstLine:0},spacing:{after:after||120},children:[new TextRun({text:t,size,bold:!!bold,font:rf(font)})]});
const cover=[new Paragraph({spacing:{before:3200},children:[]}),C('鸿图体系绘图',52,CNH,true,200),C('V2.8　发布说明',36,CNH,true,1600),C(require('./lib.js').BRAND.org,30,CN,false,120),C('2026 年 10 月 18 日',28,CN,false,120)];
add(P('**v2.8 改进三项交互：导入的流程图一键美化后框不再放大，拖动图形时自动对齐吸附，连线遇到中间的框自动绕开。**'));
add(H('一、一键美化：方框＋连线的流程图',1));
add(P('**没有分层、只有方框和箭头的图（含外框包住的流程图），一键美化改为“对齐整理”，框按文字定统一尺寸，不再放大。**'));
['**统一尺寸**：所有框取同一宽高，宽度按最长文字确定（120～220），字号归一到鸿图标准字号。','**行列对齐**：按原图的行、列聚类，同行框中线取齐、同列框中线取齐；相近的行距统一。','**保留结构**：原图的排布关系不变，只做对齐与等距，不重新打乱。','**外框收拢**：外框（子系统框）随内部内容收拢，标题、说明框随之归位。'].forEach(t=>add(LI(t)));
add(H('二、拖动吸附',1));
add(P('**拖动单个框或框选的一组图形时，靠近对齐位置自动吸附，并显示粉色参考线。**'));
add(TBL('吸附类型',['类型','说明'],[
 ['边与中线对齐','与其他图形的左、中、右，上、中、下对齐'],
 ['画布中轴','对齐整张图的横向、纵向中轴（虚线显示）'],
 ['容器中线','在层或子容器内拖动时，对齐容器的中线'],
 ['等间距','与左右（上下）相邻图形间距相等，或与已有间距相等，显示间距标记'],
 ['改尺寸','拖动框的角点改大小时，边缘对齐其他图形的边与中线'],
],[2000,6600]));
['**临时关闭**：拖动时按住 Alt 不吸附；长期开关在右侧“图面设置 › 拖动吸附”。'].forEach(t=>add(LI(t)));
add(H('三、连线自动避障',1));
add(P('**连线默认走法压过其他框时，自动改走绕行路线，不再穿过或被框遮住。**'));
['**绕行规则**：沿框外留出间距，拐弯尽量少；两框之间的多条连线分走两侧或错开 8 像素并行。','**全格式生效**：画布、PNG、PPT、Visio、draw.io 导出均按绕行后的走线输出。','**开关**：右侧“图面设置 › 连线避障”可关闭，恢复原直连走法。'].forEach(t=>add(LI(t)));
add(H('四、升级说明',1));
['**升级**：用“HongTu_v2.8.html”替换旧版文件即可，工程文件兼容；v2.7.1 的格式转换（Visio 原样转 PPT）等功能全部保留。'].forEach(t=>add(LI(t)));
(async()=>{require('fs').writeFileSync('ReleaseNotes_v2.8.docx',await Packer.toBuffer(build({title:'鸿图体系绘图 V2.8 发布说明',header:'鸿图体系绘图　V2.8 发布说明',cover,body})));console.log('ok')})();
