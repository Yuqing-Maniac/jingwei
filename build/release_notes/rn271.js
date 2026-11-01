const {P,H,TBL,build,Packer,Paragraph,TextRun,AlignmentType,rf,CNH,CN,rich}=require('./lib.js');
const body=[]; const add=(...a)=>a.forEach(x=>Array.isArray(x)?body.push(...x):body.push(x));
const LI=(t)=>new Paragraph({children:rich(t,{}),numbering:{reference:'bul',level:0},spacing:{line:330,lineRule:'auto',after:40},alignment:AlignmentType.LEFT});
const C=(t,size,font,bold,after)=>new Paragraph({alignment:AlignmentType.CENTER,indent:{firstLine:0},spacing:{after:after||120},children:[new TextRun({text:t,size,bold:!!bold,font:rf(font)})]});
const cover=[new Paragraph({spacing:{before:3200},children:[]}),C('鸿图体系绘图',52,CNH,true,200),C('V2.7.1　发布说明',36,CNH,true,1600),C(require('./lib.js').BRAND.org,30,CN,false,120),C('2026 年 10 月 17 日',28,CN,false,120)];
add(P('**v2.7.1 把“格式转换”做成可直接交付的功能：Visio 转 PowerPoint 选“保持原排版”时逐形状原样还原，字体、字号与原图一致；同时修复导入图一键美化后框被拉大、版面变乱，以及转换完成后无法继续添加文件的问题。**'));
add(H('一、格式转换（快捷键 Ctrl+Shift+O）',1));
add(H('1.1　Visio → PowerPoint 原样还原',2));
add(P('**选“保持原排版”时不再经过鸿图的分层识别，直接按 Visio 原始数据逐个形状写出**，还原内容见表 1。'));
add(TBL('原样还原内容',['类别','还原内容'],[
 ['文字','每段文字的字体（中、西文分别还原）、字号、粗体、斜体、下划线、颜色、对齐、行距、段前段后、项目符号、竖排、文字块位置与边距'],
 ['形状','位置、尺寸、旋转、翻转、几何轮廓（含圆弧、椭圆、曲线）、圆角；矩形、圆角矩形、椭圆写为 PowerPoint 原生形状，文字可直接编辑'],
 ['样式','填充色、渐变、透明度、线色、线宽、虚线、箭头样式与大小、阴影；Visio 2013 以上主题配色自动解析'],
 ['连线与组合','连接线按原走线还原（含曲线连接线），连线标签与白底保留；Visio 组合转为 PowerPoint 组合'],
 ['图片','PNG、JPG、EMF、WMF 等图片及裁切；嵌入对象按其预览图还原'],
 ['页面','每个 Visio 页面一张幻灯片，页序不变，不加入口框；背景页、隐藏图层按 Visio 显示规则处理'],
],[1800,6800]));
['**幻灯片尺寸**：默认“与原页面相同”，字号与原图完全一致；也可选“16:9 宽屏”，整页等比缩放（字号同比缩放）。','**多页尺寸不同**：以首页尺寸为幻灯片尺寸，其余页等比缩放居中，转换结果中会给出提示。','**其他格式组合**（如 PPT 转 Visio、转 draw.io、转 PNG）：按原位置和尺寸转换，形状换成最接近的鸿图形状。'].forEach(t=>add(LI(t)));
add(H('1.2　转换对话框可连续使用',2));
['**完成后直接继续添加**：上一批转换完成后，再选择或拖入文件即开始新的一批，已完成的文件自动移出，无需逐个删除。','**同一文件可重新转换**：再次加入同一文件或修改目标格式、选项后点“开始转换”，列表中的文件全部按新设置重新转换。','**设置记忆**：目标格式、排版方式、幻灯片尺寸、主题保存在本机，下次打开沿用。'].forEach(t=>add(LI(t)));
add(H('二、导入图的一键美化',1));
add(P('**导入的 Visio／PPT 图按 Ctrl+Shift+F 美化时，先把字号归一到鸿图标准字号，再按文字收紧框的尺寸**，不再出现框被拉得过大、需要逐个手调的情况。'));
['**字号归一**：首次美化时，框内文字统一为鸿图标准字号，标题、副标题、说明框分别取对应标准；之后手工调整的字号在再次美化时保留。','**框随文字定高**：多行文字的框自动加高，菱形、圆柱等形状保持比例，不再固定为单行高度。','**总宽收拢**：导入图按内容收拢总宽，避免原图过宽导致版面稀疏、字显小。','**保留原行结构**：子容器内按原图的行排列，行内等宽、等距、居中，不再把所有子框拉成一排通高的长条。','**识别层名竖条**：紧贴层框左侧的竖排层名（常见的“层名竖条＋层框”画法）识别为层标题，美化后不再残留。','**下方元素跟随**：层整体变高或变矮后，原位于下方的说明、图片等随之上移或下移。'].forEach(t=>add(LI(t)));
add(H('三、使用须知',1));
['**旧版二进制格式**：.ppt、.vsd 请先在 PowerPoint、Visio 中另存为 .pptx、.vsdx。','**字体**：原样还原沿用原图字体名，打开 PPT 的电脑需装有相应字体（如微软雅黑、宋体），否则由 PowerPoint 替换显示。','**不转换的内容**：图表、SmartArt、宏与数据链接；Visio 的跨线跳线在 PowerPoint 中不显示。','**升级**：用“HongTu_v2.7.1.html”替换旧版文件即可，工程文件与各项设置保持兼容。'].forEach(t=>add(LI(t)));
(async()=>{require('fs').writeFileSync('ReleaseNotes_v2.7.1.docx',await Packer.toBuffer(build({title:'鸿图体系绘图 V2.7.1 发布说明',header:'鸿图体系绘图　V2.7.1 发布说明',cover,body})));console.log('ok')})();
