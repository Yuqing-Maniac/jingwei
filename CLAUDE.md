# CLAUDE.md：经纬织图 JingWei ZhiTu 维护指南（给接手的 Claude）

## 1. 一句话
体系架构图／泳道图绘图工具，同一套界面代码出两种发布物：
- **网页版**：`app/` 下的模块拼成一个离线单文件 html，在 Chromium 69+／Firefox 68+ 中运行。
- **桌面版**：Electron 22.3.27 外壳（`desktop/`）加载同一界面（多注入 `app/desk/`）。不依赖系统浏览器，支持 Windows 7～11 与银河麒麟 V10（飞腾 arm64、x86_64）。

当前版本 **3.6.1**（版本号以 `desktop/package.json` 为准，网页包与桌面包共用）。桌面版首页显示的版本来自这个文件。

## 2. 目录
```
app/                 网页版源码（全部是“经典脚本”，按 build_web.py 的顺序拼接到同一作用域）
  app_body.html      页面骨架＋全部 CSS（三栏：调色板 | 画布 | 属性）
  app.js             核心：文档模型、渲染、交互、连线路由（computeRoutes/detourRoute）、一键美化、导出 PPT/VSDX/PNG/SVG、快捷键
  compact.js         紧凑排版、报告版心、导入图归一（normalizeImported）、自由图对齐（tidyFree）
  combo.js           复合图标（编队）
  standards.js       规范包：DoDAF/信息系统视图、编号、规范检查、标题栏
  xlsxexport.js      规范表格 xlsx（手写 OOXML）
  templates.js / std_templates.js   版式模板 / 11 种规范视图模板
  textgen.js         文字成图（规则解析＋可选大模型）
  refgen.js          参照生成（骨架提取＋可选大模型改写）
  importers.js       PPTX/VSDX → 织图文档（含单侧圆角识别 sideRound）
  vsdxraw.js         Visio → PPTX 原样转换（不经分层推断）
  drawio.js          draw.io 互通
  convert.js         格式转换对话框（批量）
  demo.js            启动示例图；compat.js 旧浏览器兼容层（ES5）
  country_icons.js  国别外形生成数据（build/icons/package_country.cjs），与阵营涂装独立
  icons*.js          拟物图标库（由 app/icons_src/icons_gen*.py 生成）
  desk/desk.css, desk.js   桌面版专用：标题栏、首页、本地文件读写（只在 window.jwDesk 存在时生效）
desktop/             Electron 主进程 main.js、preload.js、splash.html、brand.woff、图标；package.json 的 version 即发布版本
build/
  build_web.py       拼接 → dist/offline.html、artifact.html、（--desk）desk.html
  downlevel.js       esbuild 把内联脚本降级到 chrome69/firefox68，acorn 以 ES2019 校验
  web/package_web.py 网页版离线包 zip
  desktop/           stage.py（组装 app 目录）、build_all.py（Win 安装包/绿色版、麒麟 deb）、winexe.mjs（改 exe 图标与版本信息）、make_splash.py
  fetch_runtime.sh   下载并校验 Electron 运行时；build_all.sh 一键全部
  release_notes/     公文版式发布说明生成脚本（lib.js＋rn*.js，依赖 npm docx）
  brand.py / brand.js 机构标识读取（brand.example.json ＜ brand.local.json），见第 3 节
tests/               回归测试、QA 排查脚本、桌面版测试（见第 5 节）
docs/                规格（STD_SPEC、ICON_BRIEF、REF_BRIEF）、QA 报告、各版发布说明 docx/pdf、宣传片/教程策划
assets/brand/        图标生成脚本 icon.py（→ out/ 下 16–1024 png、ico）、svg；assets/fonts/ 得意黑
assets/country-variants/ 306项国别制作清单、公开来源、生成母版、三涂装资产与对照图册
promo/               宣传片、视频教程、海报工程（脚本含原绝对路径，见 promo/README.md）
brand.example.json   机构标识通用值；brand.local.json（gitignore）为本地真实值
_work/  dist/        （gitignore）运行时、构建中间件、发布包 / 网页版构建产物；可用 JW_WORK 改 _work 位置
```

## 3. 交付约定（用户的长期要求，必须遵守）
- **当前为独立仓库 `Yuqing-Maniac/jingwei`（原 `toolbox/jingwei`）。本文件为当前仓库维护指南。** 仓库在境外平台：不得提交型号、协议、装备参数、内部系统、真实业务数据；模板、示例、测试夹具只用虚构内容（如“边海防无人化巡逻体系”）。v3.3.2 起已把模板中的内部协议名换成通用名称，新增模板时同样处理。
- 分支 `jingwei/<简述>`，经 PR 合入 `main`；发版标签 `jingwei-v<主.次.修>`，由用户在 Releases 页面发布，`jingwei-release` 工作流自动构建并挂包。正式 Release 只上传免安装包、网页离线包、增量包和 `SHA256SUMS.txt`。资产名用唯一 ASCII（如 `jingwei_v3.3.14_windows_x64_portable.zip`），中文原名只作显示名。不上传 `.deb` 与 NSIS `.exe`。补传到已有标签时用工作流的 `upload_tag`，不新建、不移动标签。
- **离线、免安装、无需管理员权限**；运行库全部内嵌。目标机常为不联网的银河麒麟 V10（国防版，飞腾 D2000）和 Windows 7～11 内网机。
- **压缩包内文件名一律 ASCII**（用户机器上 UTF-8 与 GBK 文件名都出过乱码）。GitHub Release 的外层资产名也必须是 ASCII：中文文件名会被抹成相同的 `_vX.Y.Z_.zip`，上传返回 422。zip 用 Python zipfile 写，`package_web.py` 会做 `.encode('ascii')` 校验。
- 本地 `build/build_all.sh` 仍会生成麒麟 deb 与 Windows NSIS 安装包（安装包装到 `%LOCALAPPDATA%\Programs`，只写 HKCU）。这两类不进入正式 Release。正式交付是 Windows 绿色版 zip、麒麟免安装 zip、网页离线包和增量包。
- 发布说明用公文版式（docx＋pdf，由 build/release_notes 生成）：全角标点、一级标题汉字编号、表题在上图题在下、观点句加粗、正文仿宋、括号内楷体。
- 视频字幕：得意黑 55 号、单行。不要用用户自己的图作素材，示例统一用虚构的“边海防无人化巡逻体系”等。
- **机构标识不入库**：仓库里不得出现真实单位名称。deb 维护者、exe 公司名与版权、NSIS 卸载信息发布者、桌面版 package.json 的 author、发布说明封面与 docx 作者、海报与片尾的“出品”，一律在构建时由 `build/brand.py`（Python）／`build/brand.js`（Node）读取：先读通用值 `brand.example.json`（“经纬织图开发组”），本地存在 `brand.local.json` 时逐字段覆盖。字段：`org`（单位名称）、`copyright`（版权）、`email`（deb 维护者邮箱）。
  - **正式构建（给用户机器的安装包、发布说明）前**，先 `cp brand.example.json brand.local.json` 并填入本单位名称（用户手上有原值）。该文件已在 `.gitignore`，**不得出现在 diff 中**；CI 与 Releases 自动构建没有它，产物里是通用值。
  - 仓库里的 `desktop/package.json` author 只放通用值，`stage.py` 组装时按 brand 改写。重新生成入库的发布说明 docx／pdf 时，不要放 brand.local.json（入库文件只用通用值）。
  - 模板、示例、测试夹具里的“单位／责任单位”只用泛称（如“总体设计组”“[单位名称]”“某单位”）。
- 配音密钥（MiniMax）**只用环境变量 MM_KEY 临时传入，绝不写进文件、仓库或记忆**。
- 每次改动后重跑测试、重打全部包；版本号同步改 `desktop/package.json`，并写 CHANGELOG。

## 4. 关键技术决定与踩过的坑
**构建与兼容**
- 所有模块是经典脚本、共享一个全局作用域，**不要改成 ES module 或包进 IIFE**。`desk.js` 靠给全局函数重新赋值来接管行为（`saveFile`、`saveProject`、`checkpoint`、`loadDoc`），还会直接调用 `openForeign`、`fname`、`toast`、`buildDemo`、`fit`、`P`、`doc`、`Convert` 等。重命名这些函数时，要同步改 desk.js。
- 按钮在初始化时用 `onclick = 函数引用` 绑定，重新赋值全局函数不会影响已经绑好的处理函数，所以 desk.js 会重新绑定 `#b-save`、`#b-open`、`#b-new`。快捷键通过 `go(saveProject)` 按名字查找，会自动用上新函数。
- 麒麟上的老版浏览器：源码里不要用正则后行断言 `(?<!…)`，esbuild 不会转换，旧版火狐会解析失败导致整页白屏。CSS 不要用 `inset`（Chrome 87+）和 `:has`。运行时接口缺失由 compat.js 补齐。`build_web.py` 默认会做语法降级，加 `--modern` 可跳过。
- 不要把 U+2028 字符原样写进 JS 字符串，要用转义。
- `app/desk/desk.css` 内嵌了 brand.woff（得意黑子集）的 base64。改字体子集后要重新生成并替换。

**工程内容与渲染**
- 向 DOM 写入动态 HTML／SVG 时使用 `setMarkup`，导出 SVG 用 `safeMarkup`。DOMPurify 随离线 HTML 内嵌，不依赖网络。属性值仍须用 `esc` 转义，不能用清理器替代正确编码。
- 最近工程写入失败必须显示提示；容量不足可减少旧记录，不能先删除已有存储再尝试写入。

**连线与美化（app.js、compact.js）**
- 连线从框边中点出入；同一条边上有多条线时以中点为中心对称排开，间距不超过 24。两端中点相差 4 以内就画直线，否则画 Z 形线；只差 12 以内时也会拉直。
- 需要绕行时，`detourRoute` 在可见性网格上跑 A*，四条边都可以作出入边。参数：PAD 16、每次拐弯代价 90、通道复用惩罚 0.25×长度。
- 其余处理：通道分离、`nudgeDetours` 用排列搜索减少交叉、端口交换消除嵌套 U 形交叉、跨线弧、`labelFor` 让标签避开框和其他标签。`contentBBox` 把绕到外侧的线和标签也算进图面，否则导出会被裁掉。
- 导入的图（`n.imp`）首次一键美化时归一字号；没有分层的流程图走 `tidyFree` 做对齐整理，不放大框。
- 拖动吸附：`snapOn()` 状态存在 localStorage 的 `hongtu.snap`，按住 Alt 临时关闭。

**Visio／PPT（vsdxraw.js、importers.js）**
- 主题色：QuickStyle 颜色 0–8 对应 dk1/lt1/accent1–6/bkgnd，100–106 对应 varColor1–7；矩阵编号 100 以上走 varStyles。主题字体对比度太低时回退为 dk1。
- NURBS 曲线的节点向量是 `[C, ...knots, A, knotLast]`，并补齐（参照 libvisio 的写法）；渐变色按行继承；文字样式只回退到 style 的第 0 行。
- 单侧圆角矩形：PPT 用 custGeom 三次贝塞尔（`sideRoundPts`），Visio 用逐点轮廓，draw.io 用 `shape=mxgraph.basic.rect;topLeftStyle=rounded;…`。导回识别靠 `sideRound()`，要排除“延迟”这类 D 形图形，不要误判。
- PPT 圆角半径与画布一致，`r = min(10, h/3)`。
- 报告版心下，导入的自由图要整体收进版心宽，否则字号会掉到 6 磅左右。

**兼容性**
- 内部 id 保留旧名，用来兼容老工程文件和老设置：localStorage 的 `hongtu.*`、工程 JSON 的 `format:'hongtu'`、draw.io 属性前缀 `ht_*`。新保存的工程文件扩展名是 `.jingwei.json`。

**桌面版（desktop/main.js、app/desk）**
- 选 Electron 22.3.27，因为这是最后一个支持 Windows 7 的版本，不要随手升级。
- 窗口无边框（frame:false），header 作为拖动区，按钮设为 no-drag。对话框遮罩的 top 改为 46px，避免盖住窗口按钮。
- **界面皮肤（3.3.16）**：`app/skins.js` 与 `skins.css` 提供经典蓝、青竹、暖纸、深空，`hongtu.uiSkin` 保存选择。默认经典蓝，不自动跟随系统；图面主题独立。所有面板颜色用 CSS 变量。桌面原生对话框保持浅色。
- Windows／Linux 默认 `disableHardwareAcceleration()`，兼容国产与虚拟显卡；加 `--gpu` 可开启。启动脚本 `/usr/bin/jingwei-zhitu` 带 `--no-sandbox`（deb 里删掉了 chrome-sandbox）。启动前先用 ldd 检查缺失的库，缺了就弹窗列出。
- 拼写检查会去 redirector.gvt1.com 下载词典，必须关闭：`setSpellCheckerEnabled(false)`，并把词典下载地址指向本机无效地址。
- 免安装 zip 的顶层是 `JingWeiZhiTu/` 文件夹和唯一入口（Windows 为 `JingWeiZhiTu.exe`，麒麟为 `JingWeiZhiTu.sh`）。入口在首次运行时写桌面快捷方式。打包按 Electron 压缩包推导文件清单，缺运行库或缺图标则失败。`build/desktop/build_all.py` 仍可打 win32、麒麟 x86_64、deb；`--patch` 打增量包；网页包用 `build/web/package_web.py`。
- 所有保存都走 IPC `jw:save`，并记住上次目录。批量转换先选一次文件夹，靠 MutationObserver 监听 `#cv-msg` 出现“已完成”来收尾。
- 测试模式：设置环境变量 `JW_TEST_DIR` 后，保存／选文件夹／打开／关闭确认都不弹系统对话框。另有 `JW_TEST_OPEN`（打开哪个文件）、`JW_TEST_CLOSE`（关闭时选 save/discard/cancel）。
- Windows exe 的图标和版本信息用 resedit（纯 JS）改，不需要 wine。NSIS 安装包用 `RequestExecutionLevel user`。
- **免安装包的固定交付要求**：解压后的顶层严格只有两项——一个启动入口和一个程序文件夹，用户只需双击入口。Windows 顶层启动 EXE 与文件夹内程序 EXE 必须使用同一份 `desktop/icon.ico`，包括各尺寸图标，确保启动入口、程序和快捷方式图标一致；运行库、说明等全部放入程序文件夹。
- 麒麟上设置和最近文件保存在 `~/.config/经纬织图`，Windows 上是 `%APPDATA%\经纬织图`。
- arm64 二进制只要求 GLIBC 2.17。依赖的系统库（GTK3、NSS、CUPS、GBM 等）没法内置，因为沙箱访问不到 arm64 软件源。deb 里只写 Recommends，不写 Depends，保证离线 dpkg 能装上。

## 评审清单（独立审查逐条核对）
1. **机构标识只经 `build/brand.py`／`build/brand.js` 读取**：仓库里不得出现真实单位名称（中文全称、简称、拼音／英文名）；`brand.local.json` 不得出现在 diff 中。
2. **入库的发布说明 docx／pdf 不得带 brand.local.json 生成**：封面单位与文档作者应为通用值（“经纬织图开发组”）。
3. **示例、模板、测试夹具、宣传素材只用虚构题材**：不出现型号、协议、装备参数、内部系统、真实业务数据；“单位／责任单位”只用泛称。
4. **内部 id 不改**：localStorage 的 `hongtu.*`、工程 JSON 的 `format:'hongtu'`、draw.io 属性前缀 `ht_*`，改了会打不开老工程、丢老设置。
5. **经典脚本共享全局作用域**：不改成 ES module 或 IIFE；重命名全局函数要同步改 `app/desk/desk.js`。
6. **旧浏览器语法限制**：源码不用正则后行断言 `(?<!…)`，CSS 不用 `inset`、`:has`；`build_web.py` 的 es2019-fail 必须为 0。
7. **Electron 固定 22.3.27**（最后支持 Windows 7 的版本），不升级。
8. **压缩包内文件名一律 ASCII**、不含符号链接。Release 资产名也用唯一 ASCII，中文只作显示名；正式版不上传 `.deb` 与安装包 `.exe`。

## 5. 构建与测试

**依赖（Ubuntu 24.04 x86_64）**
```
apt-get install -y nodejs npm python3-pip nsis dpkg-dev xvfb libreoffice poppler-utils fonts-noto-cjk
pip install --break-system-packages playwright websocket-client fonttools pefile   # 测试／工具用
```
Playwright 需要 Chromium，沙箱里预装在 /opt/pw-browsers；新机器上运行 `playwright install chromium`。需要能访问 registry.npmjs.org 和 github.com（Electron 运行时、公开样例）。

**从零构建全部发布物**（以下命令都在 `jingwei/` 目录下执行）
```
npm ci                              # 按 package-lock 安装（DOMPurify 3.4.17、jszip 3.10.1、pptxgenjs 3.12.0、milsymbol 2.2.0、esbuild、acorn、asar、resedit、docx）
bash build/build_all.sh             # = fetch_runtime + build_web --desk + package_web + desktop/build_all，产物与 SHA256SUMS.txt 在 _work/dist/
```
分步命令：
- `python3 build/build_web.py`：只出网页版。
- `python3 build/desktop/build_all.py win64 deb-arm64`：只出指定平台。
- `python3 build/desktop/make_splash.py`：重新生成启动画面。
- `cd assets/brand && python3 icon.py`：重新生成图标。
- 发布说明：`cd build/release_notes && node rn321.js && soffice --headless --convert-to pdf ReleaseNotes_v3.2.1.docx`。

**测试**：测试脚本保留了开发时的绝对路径，先把旧目录结构搭起来：
```
python3 build/build_web.py --desk && python3 build/desktop/stage.py
bash build/fetch_runtime.sh && bash tests/fixtures/fetch_public.sh
bash tests/legacy_layout.sh         # 用符号链接建仓库内 _legacy/{drawtool,vfx,desk,brand_jw}；已存在的真实目录会跳过
bash tests/run_regression.sh        # 核心回归：导出、规范检查、路由、吸附、格式转换、Visio 原样转换、单侧圆角、旧浏览器模拟
```
其他测试：
- `tests/qa/*.py`：全量排查脚本（模板、导出、导入、界面），见 docs/QA_REPORT_v3.2.1.md。
- `tests/desktop/etest.py`：在 Xvfb 下启动桌面版，通过 CDP 截图并执行 `tests/desktop/scenario.py` 里的操作。用 `EXE=/usr/bin/jingwei-zhitu` 可以测已安装的 deb。
- `tests/extra/perf.py`：CPU 降速 4 倍，模拟飞腾 D2000 的速度。

## 6. 真机情况
- 网页版已在用户的银河麒麟 V10 国防版（飞腾 D2000，UKUI）上实测跑通。
- 桌面版：x86_64 deb 在沙箱里装好运行过，完整走通了文件操作。Windows 安装包、绿色版和飞腾 deb 还没有真机回报。需要重点确认：
  - Win7 32 位与 64 位能否启动；
  - 麒麟的 kysec 是否拦截；
  - 国产显卡下的显示；
  - 高 DPI 显示。

## 7. 工作方式
- 用户偏好：端到端自主执行、少打断；回复简洁、适合手机阅读、中文。
- 改了界面要截图自查，网页版和桌面版都要看，桌面版要分别看浅色和系统深色模式。改了路由或美化要跑 route_test 和 bty_test，改了导入导出要跑 conv_ui 和 raw_test。
