# Icon batch brief (shared by all icon agents)

You are adding one batch of skeuomorphic (拟物化) SVG icons to the 鸿图 diagram tool's icon library. Work autonomously; never ask questions.

## Read first (style reference — match it exactly)
- /home/claude/drawtool/icons_gen.py — original generator: gradient palette `GR`, builder `B`, helpers (glint, rotor, water, track, wheel, leds, _truck_base, mirror) and the `icon(key,name,cat)` decorator.
- /home/claude/drawtool/icons_gen_a.py — adds facility/extra palette and an oblique 3/4 helper set; reuse what helps.
- Contact sheets: /home/claude/drawtool/icon_sheet.png, icon_sheet_a.png, icon_sheet_b.png — look at them; your icons must look like the same family: lit from top-left, linear gradients, thin darker same-hue outline, highlight strokes, dark glass with glint, soft radial ground shadow under vehicles/aircraft, translucent water band under surface craft, palettes by domain (air grey-blue metal; sea haze-grey + dark-red boot topping; land olive + dark tracks/tyres; tech neutral metal + blue glass #BFE3FF→#3D86D6 + green/amber LEDs). Weapons/defeat effects may use orange/red energy accents (beams, waves, nets) with restraint.
- Existing keys you must NOT reuse: run `node -e "global.ICON_LIB=[];eval(require('fs').readFileSync('/home/claude/drawtool/icons.js','utf8').replace('const ICON_LIB','global.ICON_LIB'));for(const f of ['icons_a.js','icons_b.js'])eval(require('fs').readFileSync('/home/claude/drawtool/'+f,'utf8'));console.log(ICON_LIB.map(i=>i.key).join(' '))"` (adjust if needed) and also avoid keys from other batches (each batch has its own key prefix given in your task).

## Rules
- Do NOT edit any existing file. Create only your own generator (icons_gen_<x>.py, copy helpers rather than importing generators that write files on import) and your output `/home/claude/drawtool/icons_<x>.js` containing exactly `ICON_LIB.push(...[ {key, name, cat, svg}, ... ]);`. Do not create any other file named icons_*.js in /home/claude/drawtool (the build globs that pattern). Put scratch files in your own subfolder of /tmp/claude-0/-home-claude/4a98c7fc-ad86-519e-b225-277215eac05a/scratchpad/<x>work/.
- SVG: viewBox 0 0 96 96, self-contained <defs>, every id prefixed with the key, no <text>, <image>, href, <style>, classes or filters; valid XML; aim ≤ ~4.5 KB each.
- Each icon must be recognizable at 40 px and clearly distinct from its siblings and from existing icons (e.g. a new FPV drone must not look like the existing 四旋翼无人机 uav_quad). Distinguish by silhouette first.

## Verify (required)
Render a contact sheet with Python Playwright (chromium available): load icons.js, icons_a.js, icons_b.js, then your file; show ONLY your new icons at 96 px and 40 px with Chinese names, light background, plus a dark (#0C1622) version → /home/claude/drawtool/icon_sheet_<x>.png and icon_sheet_<x>_dark.png. Read the PNGs yourself, fix anything unrecognizable, clipped, broken or off-style, iterate until it's a cohesive professional set. Check every SVG parses with DOMParser and keys are unique overall.

Report back: file paths, count, weakest icons (brief).
