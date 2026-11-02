"""v3 fast tutorial composer.
Timeline: pain → intro_v3 → sting_01 → textgen → sting_02 → icons → sting_03 → layout → sting_04 → std → [xlsx stills] → sting_05 → finish → outro_v3
Narration placed per sentence (segment json start × mp4/json scale), BGM ducked under voice, stings mixed under intro/outro,
subtitles from subs_plan.json (Smiley Sans 55, one line). Usage: python3 make_final3.py [--crf 23] [--out path]"""
import json, subprocess, os, wave, sys
import numpy as np

T3 = '/home/claude/video/t6'; BR = f'{T3}/brand'; SR = 48000; FONTS = '/home/claude/tts/fonts'
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
CRF = arg('--crf', '21'); OUT = arg('--out', f'{T3}/tutorial_v30.mp4')

def probe(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)

def load(p, ch=1):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', str(ch), '-ar', str(SR), '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    return a.reshape(-1, ch) if ch > 1 else a

def ts(t):
    t = max(0, t); return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"

def ex(p): return os.path.exists(p)

# ---- clip list: (kind, path, dur, seg_json or None) ----
clips = []
def add_video(p, kind='clip', segjson=None):
    if ex(p): clips.append({'kind': kind, 'path': p, 'dur': probe(p), 'seg': segjson})
def add_still(p, d):
    if ex(p): clips.append({'kind': 'still', 'path': p, 'dur': d, 'seg': None})

add_video(f'{T3}/seg/pain.mp4', 'seg', f'{T3}/seg/pain.json')
add_video(f'{BR}/intro_v3.mp4', 'intro')
order = [('01', 'textgen'), ('02', 'icons'), ('03', 'layout'), ('04', 'std'), ('05', 'io'), ('06', 'finish')]
for no, s in order:
    add_video(f'{BR}/sting_{no}.mp4', 'sting')
    add_video(f'{T3}/seg/{s}.mp4', 'seg', f'{T3}/seg/{s}.json')
    if s == 'std':
        add_still(f'{T3}/seg/std_xlsx_1.png', 2.2); add_still(f'{T3}/seg/std_xlsx_2.png', 2.2)
add_video(f'{BR}/outro_v3.mp4', 'outro')

t = 0; sents = []
for c in clips:
    c['t0'] = t
    if c['seg']:
        d = json.load(open(c['seg'], encoding='utf-8')); k = c['dur'] / d['dur']
        for x in d['tl']: sents.append({'id': x['id'], 'start': t + x['start'] * k + 0.1, 'adur': x['adur']})
    t += c['dur']
TOTAL = t
print('clips:', [(os.path.basename(c['path']), round(c['dur'], 1)) for c in clips]); print('total', round(TOTAL, 1))

# ---- audio ----
N = int((TOTAL + 0.5) * SR)
voice = np.zeros(N, np.float32)
for s in sents:
    a = load(f"{T3}/audio/{s['id']}.mp3"); i = int(s['start'] * SR); voice[i:i + len(a)] += a[:max(0, N - i)]
env = np.convolve(np.abs(voice), np.ones(int(0.05 * SR)) / int(0.05 * SR), 'same')
act = np.convolve((env > 0.01).astype(np.float32), np.ones(int(0.3 * SR)), 'same') > 0
g = np.where(act, 10 ** (-19 / 20), 10 ** (-11 / 20)).astype(np.float32)
g = np.convolve(g, np.ones(int(0.2 * SR)) / int(0.2 * SR), 'same')
music = np.zeros((N, 2), np.float32)
bgm_p = f'{T3}/bgm_v3.wav' if ex(f'{T3}/bgm_v3.wav') else '/home/claude/video/tut2/bgm.wav'
intro = next((c for c in clips if c['kind'] == 'intro'), None); outro = next((c for c in clips if c['kind'] == 'outro'), None)
m0 = intro['t0'] + intro['dur'] if intro else 0; m1 = outro['t0'] if outro else TOTAL
bgm = load(bgm_p, 2); L = int((m1 - m0 + 1.0) * SR); seg = bgm[:L].copy()
fi = int(0.6 * SR); seg[:fi] *= np.linspace(0, 1, fi)[:, None]; fo = int(2.0 * SR); seg[-fo:] *= np.linspace(1, 0, fo)[:, None]
i0 = int(m0 * SR); music[i0:i0 + len(seg)] += seg[:N - i0]
music *= g[:, None]
def put(p, at, db, fade_out=0.0, maxdur=None):
    if not ex(p): return
    a = load(p, 2) * 10 ** (db / 20)
    if maxdur: a = a[:int(maxdur * SR)]
    if fade_out: n = min(len(a), int(fade_out * SR)); a[-n:] *= np.linspace(1, 0, n)[:, None]
    j = int(at * SR); music[j:j + len(a)] += a[:max(0, N - j)]
if intro: put(f'{BR}/sting_intro_v3.wav', intro['t0'], -4, 0.5, intro['dur'] + 0.6)
if outro: put(f'{BR}/sting_outro_v3.wav', outro['t0'], -4, 1.0)
mix = music + voice[:, None] * 10 ** (-0.5 / 20)
mix /= max(1.0, np.abs(mix).max() / 0.95)
with wave.open(f'{T3}/mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())

# ---- subtitles ----
plan = json.load(open(f'{T3}/subs_plan.json', encoding='utf-8')); chunks = {c['id']: c['chunks'] for c in plan['cues']}
HEAD = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Smiley Sans,55,&H00FFFFFF,&H00FFFFFF,&H00261A12,&H96000000,0,0,0,0,100,100,1,0,1,3.2,1.2,2,60,60,92,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
ev = []
for s in sents:
    cs = chunks[s['id']]; tot = sum(len(c) for c in cs); tt = s['start']
    for c in cs:
        dd = s['adur'] * len(c) / tot; ev.append(f"Dialogue: 0,{ts(tt)},{ts(tt + dd - 0.03)},Sub,,0,0,0,,{c}"); tt += dd
open(f'{T3}/subs.ass', 'w', encoding='utf-8').write(HEAD + '\n'.join(ev) + '\n')

# ---- video ----
ins = []; pre = ''
for i, c in enumerate(clips):
    if c['kind'] == 'still': ins += ['-loop', '1', '-t', f"{c['dur']:.2f}", '-i', c['path']]
    else: ins += ['-i', c['path']]
    pre += f'[{i}:v]scale=1920:1080,fps=30,setsar=1,format=yuv420p[v{i}];'
n = len(clips)
fc = pre + ''.join(f'[v{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=0[cat];[cat]ass={T3}/subs.ass:fontsdir={FONTS}[vo]'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-i', f'{T3}/mix.wav', '-filter_complex', fc, '-map', '[vo]', '-map', f'{n}:a', '-t', f'{TOTAL:.2f}',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', CRF, '-tune', 'animation', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', OUT], check=True)
print(OUT, round(probe(OUT), 1), 's', round(os.path.getsize(OUT) / 2**20, 1), 'MB')
