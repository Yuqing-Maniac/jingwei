"""v4 promo composer.
Timeline: pain → title → [sting01 text] → [sting02 ref] → [sting03 io] → [sting04 std] → [sting05 iconwall] → outro
Remotion clips carry fixed voice offsets; screen segments carry per-sentence starts in seg/<name>.json (scaled by mp4/json duration).
Usage: python3 make_promo.py [--crf 20] [--out path] [--timings]   (--timings: print BGM section args and exit)"""
import json, subprocess, os, sys, wave, re
import numpy as np

T4 = '/home/claude/video/t7'; BR = f'{T4}/brand'; SR = 48000; FONTS = '/home/claude/tts/fonts'
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
CRF = arg('--crf', '20'); OUT = arg('--out', f'{T4}/promo_v5.mp4')
ex = os.path.exists

def probe(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
def load(p, ch=1):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', str(ch), '-ar', str(SR), '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    return a.reshape(-1, ch) if ch > 1 else a
def ts(t):
    t = max(0, t); return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"

FIXED = {  # remotion clip → [(id, offset)]
    'pain_v4': [('p01', 0.40), ('p02', 3.60), ('p03', 8.45)],
    'title_v5': [('p04', 0.60)],
    'iconwall_v4': [('p16', 0.30)],
    'outro_v5': [('p17', 0.40), ('p18', 7.00), ('p19', 14.20)],
}
clips = []
def add(base, kind, seg=None):
    p = f'{BR}/{base}.mp4' if kind != 'seg' else f'{T4}/seg/{base}.mp4'
    if not ex(p): print('MISSING', p); return
    clips.append({'base': base, 'kind': kind, 'path': p, 'dur': probe(p), 'seg': seg})
add('pain_v4', 'rem'); add('title_v5', 'rem')
for n, s in [('01', 'text'), ('02', 'link'), ('03', 'ref'), ('04', 'io'), ('05', 'std')]:
    add(f'sting_v5_{n}', 'sting'); add(s, 'seg', f'{T4}/seg/{s}.json')
add('sting_v5_06', 'sting'); add('iconwall_v4', 'rem'); add('outro_v5', 'rem')

t = 0; sents = []
for c in clips:
    c['t0'] = t
    if c['seg']:
        d = json.load(open(c['seg'], encoding='utf-8')); k = c['dur'] / d['dur']
        for x in d['tl']: sents.append({'id': x['id'], 'start': t + x['start'] * k + 0.08})
    for i, off in FIXED.get(c['base'], []): sents.append({'id': i, 'start': t + off})
    t += c['dur']
TOTAL = t
for s in sents: s['adur'] = probe(f"{T4}/audio/{s['id']}.mp3")
sents.sort(key=lambda s: s['start'])
get = lambda b: next((c for c in clips if c['base'] == b), None)
pain, title, outro = get('pain_v4'), get('title_v5'), get('outro_v5')
bgm_args = dict(pain_end=pain['t0'] + pain['dur'] if pain else 13.6, title_end=title['t0'] + title['dur'] if title else 19.6,
                outro_start=outro['t0'] if outro else TOTAL - 19.5, final_hit=(outro['t0'] + 14.47) if outro else TOTAL - 7.4, length=TOTAL)
print('clips:', [(c['base'], round(c['dur'], 2)) for c in clips]); print('total', round(TOTAL, 2))
print('BGM: --pain-end %.2f --title-end %.2f --outro-start %.2f --final-hit %.2f --length %.2f' % tuple(bgm_args[k] for k in ['pain_end', 'title_end', 'outro_start', 'final_hit', 'length']))
if '--timings' in sys.argv: sys.exit(0)

# ---------------- audio ----------------
N = int((TOTAL + 0.3) * SR)
voice = np.zeros(N, np.float32)
for s in sents:
    a = load(f"{T4}/audio/{s['id']}.mp3"); i = int(s['start'] * SR); voice[i:i + len(a)] += a[:max(0, N - i)]
env = np.convolve(np.abs(voice), np.ones(int(0.05 * SR)) / int(0.05 * SR), 'same')
act = np.convolve((env > 0.01).astype(np.float32), np.ones(int(0.3 * SR)), 'same') > 0
g = np.where(act, 10 ** (-15 / 20), 10 ** (-6 / 20)).astype(np.float32)
g = np.convolve(g, np.ones(int(0.2 * SR)) / int(0.2 * SR), 'same')
music = np.zeros((N, 2), np.float32)
bp = f'{T4}/bgm_v5.wav'
if ex(bp):
    b = load(bp, 2)[:N]; music[:len(b)] += b
music *= g[:, None]
sfx = np.zeros((N, 2), np.float32)
for c in clips:
    for cand in [f"{BR}/sfx_{c['base']}.wav", f"{BR}/{c['base']}.wav", f"{BR}/sfx_{c['base'].replace('_v4', '')}.wav"]:
        if ex(cand):
            a = load(cand, 2) * 10 ** (-5 / 20); j = int(c['t0'] * SR); sfx[j:j + len(a)] += a[:max(0, N - j)]; break
mix = music + sfx * np.where(act, 0.55, 1.0)[:, None] + voice[:, None] * 10 ** (-0.5 / 20)
mix /= max(1.0, np.abs(mix).max() / 0.95)
with wave.open(f'{T4}/mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())

# ---------------- subtitles: one line per cue, ≤ 17 chars ----------------
txt = {s['id']: s['text'] for s in json.load(open(f'{T4}/script.json', encoding='utf-8'))}
def chunks(s, mx=17):
    parts = [p for p in re.split(r'(?<=[，。；：！？、,])', s) if p.strip()]
    out, cur = [], ''
    for p in parts:
        if len(cur) + len(p) <= mx: cur += p
        else:
            if cur: out.append(cur)
            while len(p) > mx: out.append(p[:mx]); p = p[mx:]
            cur = p
    if cur: out.append(cur)
    return [re.sub(r'[，。；：、,]$', '', o).strip() for o in out]
HEAD = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Smiley Sans,55,&H00FFFFFF,&H00FFFFFF,&H00261A12,&H96000000,0,0,0,0,100,100,1,0,1,3.2,1.2,2,60,60,64,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
ev = []
for s in sents:
    cs = chunks(txt[s['id']]); tot = sum(len(c) for c in cs); tt = s['start']
    for c in cs:
        dd = s['adur'] * len(c) / tot; ev.append(f"Dialogue: 0,{ts(tt)},{ts(tt + dd - 0.03)},Sub,,0,0,0,,{c}"); tt += dd
open(f'{T4}/subs.ass', 'w', encoding='utf-8').write(HEAD + '\n'.join(ev) + '\n')

# ---------------- video ----------------
ins = []; pre = ''
for i, c in enumerate(clips):
    ins += ['-i', c['path']]
    pre += f'[{i}:v]scale=1920:1080,fps=30,setsar=1,format=yuv420p[v{i}];'
n = len(clips)
fc = pre + ''.join(f'[v{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=0[cat];[cat]ass={T4}/subs.ass:fontsdir={FONTS}[vo]'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-i', f'{T4}/mix.wav', '-filter_complex', fc, '-map', '[vo]', '-map', f'{n}:a', '-t', f'{TOTAL:.2f}',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', CRF, '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT], check=True)
print(OUT, round(probe(OUT), 1), 's', round(os.path.getsize(OUT) / 2**20, 1), 'MB')
