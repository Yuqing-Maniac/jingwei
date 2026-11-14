# 经纬织图 JingWei ZhiTu

体系架构图／泳道图绘制工具：分层框架、拟物化装备图标、文字成图、一键美化，PowerPoint／Visio／draw.io 打开与互转。全部组件内置，离线运行。

## 两种形态

| 形态 | 文件 | 运行方式 |
|---|---|---|
| 网页版（单文件） | `JingWeiZhiTu_v<版本>.html` | 用 Chromium 69+／Firefox 68+ 内核浏览器打开，无需安装 |
| 桌面版（自带运行环境，不需要浏览器） | Windows 绿色版 zip；银河麒麟免安装 zip | 解压后双击或执行启动脚本，无需安装 |

## 支持平台

- Windows 7 SP1、8、10、11（x64 与 32 位 x86）
- 银河麒麟桌面操作系统 V10（含国防版）：飞腾 arm64（D2000 已实测）、x86_64
- 网页版另可在任何 Chromium 69+／Firefox 68+ 浏览器中使用

## 主要功能

- **界面皮肤**：经典蓝、青竹、暖纸、深空，工具栏和桌面首页均可切换，自动记住选择，不改变图面主题与导出配色。
- **桌面启动**：经纬交织启动动画，默认全屏；点击「退出全屏」或按 F11 返回窗口。
- **绘图**：分组带、层（泳道）、子容器；基础形状、流程图形、箭头；667 个写实图标（含后勤、能源、医疗、海洋、航天、无人、制造、数据治理、人工智能等），均支持原色／红方／蓝方局部涂装与编队复合图标。
- **图形编辑**：普通图形可旋转；光电／雷达扇区可调方向、开角、半径，防御圈可调范围与线型。图标文字支持紧贴和独立拖动；重叠图形可上移／下移一层或置顶／置底。纯图标的选择框贴近实际可见图形，排除透明留白。
- **文字成图**（Ctrl+Shift+G）：粘贴文字或 Markdown，自动生成分层架构图。
- **参照生成**（Ctrl+Shift+L）：以一张好图为参照，填入新项目内容生成同款新图；可接内网 OpenAI 兼容大模型，也可离线。
- **一键美化**（Ctrl+Shift+F）：对齐、等距；连线从框边中点出入、同边多线对称排布、绕开中间的框且拐弯最少；拖动吸附。
- **链路类型**：选中连线后按 S，在关联、数据流、指令流、有线／光纤、无线／数据链、卫通链路、告警、时统之间循环。这一步可以撤销。数字键 1 到 6 直接选择前六类。告警是红色短虚线，时统是琥珀色长虚线。正在输入文字时不切换。
- **图例**：页面上出现连线后自动添加。图例只列本页用到的状态和链路类型。增删或切换类型后，图例跟着变。图例可以拖动，导出时一并带上。手动删掉后不再自动补回。
- **规范视图**：DoDAF（OV-1、OV-2、OV-5b、SV-1、SV-4）与信息系统六类架构视图，自动编号、规范检查、标题栏、规范表格（xlsx）。
- **格式互通**（Ctrl+Shift+O）：打开 .pptx／.vsdx／.drawio；导出 PNG（透明、报告插图）、PPT、Visio、draw.io、SVG；Visio 批量转 PPT 时字体字号原样还原。
- **报告版心**：按版心宽与图内字号排版，插入 Word 即为版心宽。

## 中美外形图册

原306项国别筛选清单及新增型号／任务图标的制作记录与对照图册在 [assets/country-variants](assets/country-variants/README.md)。图标面板可选中国／美国外形，默认中国红、美国蓝；节点属性仍可单独改色。无可靠来源的项目保留通用外形，图册逐项显示任务示意和待复核限制。

依次运行 `node build/icons/package_country.cjs` 和 `node build/icons/package_recon.cjs` 更新运行时，再运行 `node build/icons/country_atlas.cjs` 生成 `_work/country-atlas.html` 单文件离线图册。

## 下载

当前源码版本是 3.6.4。版本号在 `desktop/package.json`，与根目录 `package.json` 相同。桌面版首页的版本号读这个字段。

3.5.2 的草稿发布包含两份免安装包。解压后顶层是 `JingWeiZhiTu` 文件夹和唯一入口，只运行那个入口。

- `jingwei_v3.5.2_windows_x64_portable.zip`（Windows 10／11，64 位，入口 `JingWeiZhiTu.exe`）
- `jingwei_v3.5.2_kylin_arm64_portable.zip`（银河麒麟 V10，ARM64，入口 `JingWeiZhiTu.sh`）
- `SHA256SUMS.txt`

Windows 32 位、麒麟 x86_64、离线网页包和增量包这次没有放进发布。打包脚本仍能构建它们。Electron 22.3.27 能在 Windows 7 SP1 x64 上运行，这次没有单独的 Win7 包，也没有 Win7 真机测试。

以下是已发布的 3.3.15／3.3.14 下载说明。

到仓库 Releases 页面下载标签 `jingwei-v<版本>`。文件名是唯一 ASCII，中文只作显示名。发布时上传免安装 zip、网页离线 zip、增量 zip 和 `SHA256SUMS.txt`。

`jingwei-v3.3.15` 这一版只有 `jingwei_v3.3.15_incremental.zip` 和 `SHA256SUMS.txt`。完整免安装包在 `jingwei-v3.3.14`。

- `jingwei_v3.3.14_windows_x64_portable.zip`
- `jingwei_v3.3.14_windows_x86_portable.zip`
- `jingwei_v3.3.14_kylin_arm64_portable.zip`
- `jingwei_v3.3.14_kylin_x86_64_portable.zip`
- `jingwei_v3.3.14_web_offline.zip`
- `jingwei_v3.3.14_incremental.zip`
- `SHA256SUMS.txt`

## 使用

- **3.5.2 Windows**：解压 `jingwei_v3.5.2_windows_x64_portable.zip`，双击旁边的 `JingWeiZhiTu.exe`。
- **3.5.2 银河麒麟 ARM64**：解压 `jingwei_v3.5.2_kylin_arm64_portable.zip`，执行 `sh JingWeiZhiTu.sh`。
- **Windows 绿色版（3.3.14）**：解压 `jingwei_v3.3.14_windows_x64_portable.zip` 或 `jingwei_v3.3.14_windows_x86_portable.zip`，双击 `JingWeiZhiTu/JingWeiZhiTu.exe`。
- **银河麒麟免安装**：解压 `jingwei_v3.3.14_kylin_arm64_portable.zip` 或 `jingwei_v3.3.14_kylin_x86_64_portable.zip`，进入 `JingWeiZhiTu` 后执行 `sh start.sh`。
- **网页版**：解压 `jingwei_v3.3.14_web_offline.zip`，双击 `JingWeiZhiTu_v3.3.14.html`。
- **增量升级**：在 3.3.14 桌面版标题栏点「增量升级」，选择 `jingwei_v3.3.15_incremental.zip`。见 `docs/INCREMENT.md`。

使用说明见 `docs/release-notes/Guide_v3.3.pdf`。3.3.15 的链路类型、图例和下载文件以本页为准。

## 常用快捷键

Ctrl+S 保存（桌面版直接写回当前文件），Ctrl+Shift+S 另存为（桌面版），Ctrl+O 打开，Ctrl+E 导出，F1 全部快捷键，F11 全屏（桌面版）。选中连线后按 S 循环链路类型。正在输入文字时 S 不切换类型。

## 从源码构建

见 `CLAUDE.md` 第 5 节。本地完整构建是 `npm ci && bash build/build_all.sh`，产物在 `_work/dist/`。

只构建这一版发布的两份免安装包：`python build/desktop/build_all.py --portable-only win64 kylin-arm64`。加上 `win32`、`kylin-amd64` 可打另外两个平台。`--patch` 打增量包。网页版用 `python build/web/package_web.py`。这些路径不需要 NSIS 或 dpkg。Windows 安装包要额外加 `--installers`。前置为 `npm ci` 和已校验的 Electron 22.3.27 运行时。

拉取请求上的 `jingwei-ci` 会构建界面，并运行 `tests/run_regression.sh`。完整打包在发布标签 `jingwei-v*` 或手动运行 `jingwei-release` 时进行。不要在每个拉取请求上再运行完整打包。
