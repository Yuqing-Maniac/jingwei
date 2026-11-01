# 宣传片、视频教程与海报工程

只入库脚本与源码；录屏帧、配音 mp3、配乐 wav、成片 mp4、海报成图都不入库（可重新生成）。
**脚本保留开发时的绝对路径**（/home/claude/video/…、/home/claude/drawtool/…）。复现时先在仓库根目录执行 `bash tests/legacy_layout.sh` 建好旧目录结构，再把本目录内容放到 `/home/claude/video/` 下对应位置（t6 → video/t6，t7 → video/t7，remotion → video/brand/remotion，rec.py → video/rec.py）。

| 目录 | 内容 | 成片 |
|---|---|---|
| `t6/` | v3.1 视频教程：章节录屏（harness.py＋ch_*.py）、配音（tts.py）、字幕与合成（make_final3.py） | 经纬织图_视频教程_v3.1.mp4（约 5 分 26 秒） |
| `t7/` | v3.2 宣传片：章节录屏、配音、配乐合成（gen_bgm_v4.py）、音效（gen_sfx_outro.py）、合成（make_promo.py）；mock4.py＋reply.txt 是参照生成演示用的假大模型 | 经纬织图_宣传片_v3.2.mp4（约 2 分 4 秒） |
| `remotion/` | 片头、章节转场、图标墙、片尾（Remotion 4.0.250；v5.tsx 为 v3.2 宣传片） | render6.sh／render7.sh 渲染到 t6／t7 的 brand/ |
| `poster/` | 早期推广海报（html＋截图脚本） | — |
| `rec.py` | 录屏核心（逐帧截图＋鼠标指针注入） | — |

## 流程（以 t7 宣传片为例）
1. `cd promo/remotion && npm i && bash render7.sh`（public/fonts 需放入 `assets/fonts/SmileySans-Oblique.ttf`）
2. 配音：`MM_KEY=<MiniMax 密钥> python3 t7/tts.py`。**密钥只用环境变量传入，不写入任何文件。**音色 presenter_male、语速 1.12、情绪 happy。
3. 录屏：先 `python3 t7/mock4.py &`（参照生成章节需要），再 `python3 t7/harness.py <text|link|ref|io|std>`（最多同时两路）。
4. 配乐：`python3 t7/make_promo.py --timings` 取时间点 → `python3 t7/gen_bgm_v4.py <时间参数> --out t7/bgm_v5.wav`
5. 合成：`python3 t7/make_promo.py --crf 26 --out 成片.mp4`
字幕规范：得意黑 Smiley Sans 55 号，每条只一行。
