# v3 fast tutorial — chapter brief (shared)

We are re-recording a FAST, DYNAMIC ~5-minute Chinese tutorial for 「鸿图体系绘图」 (offline HTML diagram editor at /home/claude/drawtool/offline.html). Narration is DONE: /home/claude/video/t3/script.json (42 sentences, ids 001–042, with chapters) and one MiniMax mp3 per id in /home/claude/video/t3/audio/ (speed 1.12, punchy). Read every sentence of your chapter; the picture must show exactly what each sentence says, AT THE MOMENT it is said. Work autonomously; never ask questions.

## Style — this is the main change from the previous (slow) version
- Fast and kinetic: quick, confident cursor moves (r.move dur 0.25–0.45 s, drags 0.5–0.9 s), no idle hovering, no long holds. Something should visibly change every 1–2 seconds.
- Use in-app camera moves for energy: animate the canvas `view` (zoom-in to the element being discussed, then zoom back out) — e.g. copy the `zoomto` helper idea from /home/claude/video/t2/ch_layout.py (animates view.x/y/k then applyView()). Zoom to 140–180 % on the action, back to fit for overviews.
- Key-hint overlay r.keys('Ctrl + Shift + F　一键美化') every time a shortcut is pressed (the overlay is large and centred top — it's part of the dynamism).
- Keep actions within each sentence's audio duration; overruns > 0.5 s are not acceptable in this version (harness prints OVERRUN). The harness gap between sentences is only 0.22 s.

## Read first
- /home/claude/video/t3/harness.py (docstring = API; usage `python3 /home/claude/video/t3/harness.py <name> [--dry] [--fast]`; outputs /home/claude/video/t3/seg/<name>.mp4 + .json; only 2 recordings at once, it queues automatically).
- /home/claude/video/rec.py helpers; working examples from the previous version: /home/claude/video/t2/ch_*.py (origin, idea, textgen, palette, layout, finish, outro) — reuse their tricks (port-drag with elementFromPoint check, time-based moves under CPU load, voice-input stub, template card clicks with `>> visible=true`, select_option for <select>).
- App features (grep app.js, combo.js, standards.js, xlsxexport.js, templates.js, std_templates.js, textgen.js for ids): header #b-new #b-beauty #b-cross #b-text #b-tpl #b-form(编队) #b-std(规范) #b-theme #b-export; shortcuts Ctrl+Shift+F/X/G/M/B/K, Ctrl+G 组合, Ctrl+Shift+U 拆分, Ctrl+E, Ctrl+K, F1, F2; formation dialog #cb-q #cb-icons [data-k] #cb-pats [data-p] #cb-n #cb-frame #cb-ok; standards panel (nothing selected) #std-view #std-codes #std-num #std-check #std-tb #std-xlsx and checker dialog #std-fix #std-re #std-close, rows with 「定位」 buttons; link properties inputs id std-* ; templates include 9 regular + 5 standard views (std-ov1, std-ov2, std-ov5b, std-sv1, std-sv4; names 「OV-1 高层作战概念图」…). The initial diagram on load is 「边海防无人化巡逻体系」 (free drawing, no view set).
- Page globals for setup via r.page.evaluate: doc, P(), mkNode, uid, beautify, render, fit, loadDoc, buildDemo, TEMPLATES, ICON_LIB, view, applyView, sel, selLink, Combo, Std.

## Deliverable
/home/claude/video/t3/ch_<name>.py (IDS, setup, ACTIONS). Iterate with `--dry --fast`, LOOK at screenshots you take inside actions, then `--dry` for timing, then record for real. Check ~6 stills from the mp4. Don't edit harness.py, rec.py, the app, or other agents' files. Report duration and any notes for the composer (e.g. final screen state).
