"""SFX for OutroV5 (impacts at the OT beats, riser into the lockup)."""
import sys; sys.path.insert(0, '/home/claude/video/t7')
import numpy as np
from gen_bgm_v4 import impact_wave, riser_wave, SR
from scipy.io import wavfile
OT = dict(file=20, inst=42, off=60, win=83, kylin=106, ft=134, run=167, out1=207, kw=[214, 239, 259, 282, 303, 322], title=434)
N = int(19.6 * SR); out = np.zeros((N, 2))
def put(fr, w, g):
    i = int(fr / 30 * SR); out[i:i + len(w)] += w[:max(0, N - i)] * g
put(OT['file'] + 6, impact_wave(3), 0.55)
for k in ['inst', 'off']: put(OT[k], impact_wave(4), 0.35)
for k in ['win', 'kylin', 'ft']: put(OT[k], impact_wave(5), 0.25)
put(OT['run'], impact_wave(6), 0.3)
for t in OT['kw']: put(t, impact_wave(7), 0.22)
r = riser_wave(1.2, 9); put(OT['title'] - 36, r, 0.3)
put(OT['title'], impact_wave(2), 0.9)
out /= max(1, np.abs(out).max() / 0.9)
wavfile.write('/home/claude/video/t7/brand/sfx_outro_v5.wav', SR, (out * 32767).astype(np.int16))
print('ok')
