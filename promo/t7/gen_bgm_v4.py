#!/usr/bin/env python3
"""BGM v4 for the 105 s 鸿图体系绘图 v2.5 promo -- fully synthesised (numpy/scipy), timings from CLI.

  python3 gen_bgm_v4.py --pain-end 13.6 --title-end 19.6 --outro-start 85.0 --final-hit 97.1 --length 105.0 \
      --out /home/claude/video/t4/bgm_v4.wav

Sections: dark tension (0..pain-end, D minor, suck-back 0.25 s before pain-end) -> impact + D major title lift
-> driving groove (bar grid anchored at title-end, tempo snapped into 124-128 BPM so whole bars fit up to
outro-start) -> anthemic lift + riser -> final impact + sustained chord, fade to length.
Synthesis blocks are copied from gen_bgm_v3.py (pads, plucks, kick/clap/hats, bass, riser, impact, reverb, mix, loudnorm).
"""
import zlib, argparse, json, os, re, subprocess, sys
from functools import lru_cache
import numpy as np
import scipy.signal as ss
from scipy.io import wavfile

SR = 48000
BPM = 126.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
E8 = BEAT / 2
S16 = BEAT / 4


def mtof(m):
    return 440.0 * 2 ** ((np.asarray(m, dtype=np.float64) - 69) / 12)


def sos_f(kind, fc, order=4, x=None, axis=0):
    sos = ss.butter(order, fc, btype=kind, fs=SR, output="sos")
    return sos if x is None else ss.sosfilt(sos, x, axis=axis).astype(np.float32)


def peaking(x, f0, gain_db, q):
    A = 10 ** (gain_db / 40)
    w = 2 * np.pi * f0 / SR
    al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]
    a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return ss.lfilter(b, a, x, axis=0).astype(np.float32)


# ---------------------------------------------------------------- chords
CH = {  # pad voicing, arp tones, bass root (midi)
    "D":    ([50, 57, 62, 66],     [62, 66, 69, 74], 38),
    "Dadd": ([50, 57, 62, 64, 66], [62, 66, 69, 76], 38),
    "A":    ([52, 57, 61, 64],     [64, 69, 73, 76], 33),
    "Bm":   ([50, 54, 59, 62],     [62, 66, 71, 74], 35),
    "G":    ([50, 55, 59, 62],     [62, 67, 71, 74], 31),
    "Gmaj7": ([50, 55, 59, 66],    [62, 67, 71, 78], 31),
}


# ---------------------------------------------------------------- voices
@lru_cache(maxsize=None)
def pad_wave(notes, dur, att, rel, seed):
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    env = np.ones(n)
    na = int(att * SR)
    env[:na] = 0.5 - 0.5 * np.cos(np.pi * np.arange(na) / na)
    ns = int(dur * SR)
    nr = n - ns
    env[ns:] = 0.5 + 0.5 * np.cos(np.pi * np.arange(nr) / nr)
    r = np.random.default_rng(seed)
    out = np.zeros((n, 2))
    det = [(-11, -3, 6), (-6, 3, 11)]
    for m in notes:
        f = float(mtof(m))
        K = int(min(14, 2600 // f))
        k = np.arange(1, K + 1)[:, None]
        amp = 1.0 / k ** 1.25
        for ch in range(2):
            for c in det[ch]:
                fq = f * 2 ** (c / 1200)
                ph = r.uniform(0, 2 * np.pi)
                lfo = 1 + 0.0015 * np.sin(2 * np.pi * r.uniform(0.1, 0.3) * t + r.uniform(0, 6))
                phase = 2 * np.pi * np.cumsum(fq * lfo) / SR + ph
                out[:, ch] += (amp * np.sin(k * phase[None, :])).sum(0) / 3
    out *= env[:, None] / len(notes)
    return out


@lru_cache(maxsize=None)
def pluck_wave(m, soft):
    f = float(mtof(m))
    n = int(1.9 * SR)
    t = np.arange(n) / SR
    idx = (1.1 + 0.7 * (1 - soft)) * np.exp(-t / 0.09) + 0.08
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    y += 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.15)
    env = (1 - np.exp(-t / 0.004)) * np.exp(-t / 0.42)
    env[-4000:] *= np.linspace(1, 0, 4000)
    return y * env


@lru_cache(maxsize=None)
def pluck16_wave(m, bright):
    """short plucked tone for 16th-note arpeggios (dry, dies in ~0.3 s)."""
    f = float(mtof(m))
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    idx = (0.5 + 0.6 * bright) * np.exp(-t / 0.035) + 0.04
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    y += 0.2 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.06)
    env = (1 - np.exp(-t / 0.002)) * np.exp(-t / 0.115)
    env[-2500:] *= np.linspace(1, 0, 2500)
    return y * env


@lru_cache(maxsize=None)
def kick_wave():
    """tight punchy kick: fast pitch drop, ~110 ms body, 4 ms click."""
    n = int(0.26 * SR)
    t = np.arange(n) / SR
    f = 48 + 130 * np.exp(-t / 0.018)
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = (1 - np.exp(-t / 0.0015)) * np.exp(-t / 0.075)
    y = np.sin(ph) * env
    r = np.random.default_rng(7)
    click = sos_f("high", 900, 2, sos_f("low", 3000, 2, r.standard_normal(n))) * np.exp(-t / 0.003) * 0.12
    y = y + click
    y[-800:] *= np.linspace(1, 0, 800)
    return sos_f("low", 4000, 2, y)


@lru_cache(maxsize=None)
def clap_wave(v):
    """clap/snare: 3 fast noise bursts + tail (noise above 4 kHz, body ~200 Hz) -> little energy in 1-4 kHz."""
    r = np.random.default_rng(300 + v)
    n = int(0.24 * SR)
    t = np.arange(n) / SR
    x = r.standard_normal(n)
    x = ss.sosfilt(ss.butter(2, [4200, 9800], btype="band", fs=SR, output="sos"), x)
    env = np.zeros(n)
    for k, d in enumerate((0.0, 0.011, 0.023)):
        i = int(d * SR)
        env[i:] += (0.55 if k < 2 else 1.0) * np.exp(-(t[:n - i]) / (0.006 if k < 2 else 0.055))
    body_f = 170 + 110 * np.exp(-t / 0.02)
    body = np.sin(2 * np.pi * np.cumsum(body_f) / SR) * np.exp(-t / 0.05) * 0.8
    y = x * env + body
    y[-600:] *= np.linspace(1, 0, 600)
    return y


@lru_cache(maxsize=None)
def hat_wave(v):
    r = np.random.default_rng(200 + v)
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    x = ss.sosfilt(ss.butter(2, [6500, 11000], btype="band", fs=SR, output="sos"), r.standard_normal(n))
    env = (1 - np.exp(-t / 0.0008)) * np.exp(-t / 0.012)
    env[-200:] *= np.linspace(1, 0, 200)
    return x * env


@lru_cache(maxsize=None)
def bass_wave(m, dur, decay):
    f = float(mtof(m))
    n = int((dur + 0.06) * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * 2 * f * t) + 0.22 * np.sin(2 * np.pi * 3 * f * t)
    env = (1 - np.exp(-t / 0.005)) * np.exp(-t / decay)
    ns = int(dur * SR)
    env[ns:] *= np.linspace(1, 0, n - ns)
    return y * env


@lru_cache(maxsize=None)
def riser_wave(dur, seed=1):
    """short riser: gated noise band 4.5-11 kHz (rate 4->20 Hz) + rising sine sweep 160->900 Hz; stereo; peak-normalised."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    u = t / dur
    r = np.random.default_rng(seed)
    out = np.zeros((n, 2))
    gate_ph = 2 * np.pi * np.cumsum(4 + 16 * u ** 1.5) / SR
    gate = 0.65 + 0.35 * np.sin(gate_ph)
    sos = ss.butter(2, [4500, 11000], btype="band", fs=SR, output="sos")
    sw_ph = 2 * np.pi * np.cumsum(160 * (900 / 160) ** u) / SR
    tone = np.sin(sw_ph) + 0.3 * np.sin(2 * sw_ph)
    env = u ** 2.2
    for ch in range(2):
        out[:, ch] = ss.sosfilt(sos, r.standard_normal(n)) * gate * env * 1.0 + 0.35 * tone * env * (0.9 if ch else 1.0)
    fo = int(0.012 * SR)
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    out[:fo] *= np.linspace(0, 1, fo)[:, None]
    return out / np.abs(out).max()


@lru_cache(maxsize=None)
def impact_wave(seed=2):
    """impact hit: pitch-dropping sub + short noise crash (>5 kHz) + low thump; peak-normalised stereo."""
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    f = 38 + 60 * np.exp(-t / 0.12)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - np.exp(-t / 0.002)) * np.exp(-t / 0.42)
    r = np.random.default_rng(seed)
    out = np.zeros((n, 2))
    sos = ss.butter(2, [5000, 12000], btype="band", fs=SR, output="sos")
    for ch in range(2):
        cr = ss.sosfilt(sos, r.standard_normal(n)) * (1 - np.exp(-t / 0.002)) * np.exp(-t / 0.33)
        out[:, ch] = sub * 1.0 + 0.45 * cr
    out[-1500:] *= np.linspace(1, 0, 1500)[:, None]
    return out / np.abs(out).max()


@lru_cache(maxsize=None)
def shaker_wave(v):
    r = np.random.default_rng(100 + v)
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    x = r.standard_normal(n)
    sos = ss.butter(2, [3800, 8500], btype="band", fs=SR, output="sos")
    x = ss.sosfilt(sos, x)
    env = (1 - np.exp(-t / 0.010)) * np.exp(-t / 0.035)
    env[-500:] *= np.linspace(1, 0, 500)
    return x * env


@lru_cache(maxsize=None)
def air_wave(m, dur):
    f = float(mtof(m))
    n = int((dur + 1.5) * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) + 0.12 * np.sin(2 * np.pi * 2 * f * t)
    y *= 1 + 0.04 * np.sin(2 * np.pi * 4.7 * t)
    na = int(1.4 * SR)
    env = np.ones(n)
    env[:na] = 0.5 - 0.5 * np.cos(np.pi * np.arange(na) / na)
    ns = int(dur * SR)
    env[ns:] = 0.5 + 0.5 * np.cos(np.pi * np.arange(n - ns) / (n - ns))
    return y * env


def swell_wave(dur, seed=5, curve=2.2):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros((n, 2))
    sos = ss.butter(2, [350, 2600], btype="band", fs=SR, output="sos")
    t = np.linspace(0, 1, n)
    env = t ** curve * (1 - 0.0 * t)
    env[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
    for ch in range(2):
        out[:, ch] = ss.sosfilt(sos, r.standard_normal(n)) * env
    return out


# ---------------------------------------------------------------- reverb
def make_ir(rt=2.6, pre=0.022, seed=11):
    r = np.random.default_rng(seed)
    n = int((rt * 1.15 + pre) * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2))
    for ch in range(2):
        x = r.standard_normal(n)
        lo = sos_f("low", 2200, 2, x) * np.exp(-t * 6.9 / rt)
        hi = sos_f("low", 6500, 2, x) * np.exp(-t * 6.9 / (rt * 0.45))
        y = lo + 0.5 * hi
        y = sos_f("high", 180, 2, y)
        k = int(pre * SR)
        y = np.concatenate([np.zeros(k), y[:-k]])
        # soft early build-up
        y *= (1 - np.exp(-t / 0.03))
        ir[:, ch] = y
    ir /= np.sqrt((ir ** 2).sum(0, keepdims=True))
    return ir


def reverb(x, ir):
    out = np.zeros(x.shape, np.float32)
    for ch in range(2):
        out[:, ch] = ss.oaconvolve(x[:, ch], ir[:, ch].astype(np.float32), mode="full")[: len(x)]
    return out


# ---------------------------------------------------------------- Canvas
class Canvas:
    def __init__(self, n):
        self.n = n
        self.s = {}

    def stem(self, name):
        if name not in self.s:
            self.s[name] = np.zeros((self.n, 2), dtype=np.float32)
        return self.s[name]

    def add(self, name, t, w, gain=1.0, pan=0.0):
        i = int(round(t * SR))
        if i >= self.n or i + len(w) <= 0:
            return
        b = self.stem(name)
        j0 = max(i, 0)
        j1 = min(i + len(w), self.n)
        seg = w[j0 - i: j1 - i]
        if seg.ndim == 1:
            th = (pan + 1) * np.pi / 4
            b[j0:j1, 0] += (seg * gain * np.cos(th)).astype(np.float32)
            b[j0:j1, 1] += (seg * gain * np.sin(th)).astype(np.float32)
        else:
            b[j0:j1] += (seg * gain).astype(np.float32)


def rms_db(x):
    return 10 * np.log10(np.mean(np.asarray(x, dtype=np.float64) ** 2) + 1e-20)


def scale_to(x, target_db, active_thresh_db=-60):
    """scale so RMS over active (non-silent, 100 ms blocks) region hits target."""
    m = x.mean(1)
    blk = len(m) // 4410 * 4410
    p = (m[:blk].reshape(-1, 4410).astype(np.float64) ** 2).mean(1)
    act = p > 1e-9
    if act.sum() == 0:
        return x
    cur = 10 * np.log10(p[act].mean())
    return x * (10 ** ((target_db - cur) / 20))


# ---------------------------------------------------------------- mix & master
def duck_curve(n, kick_times, depth=0.2, tau=0.11):
    d = np.zeros(n)
    k = np.exp(-np.arange(int(0.45 * SR)) / (tau * SR))
    for tk in kick_times:
        i = int(tk * SR)
        if i < n:
            m = min(len(k), n - i)
            d[i:i + m] += k[:m]
    d = ss.sosfilt(ss.butter(2, 35, "low", fs=SR, output="sos"), np.minimum(d, 1.0))  # no instant step -> no click
    return 1 - depth * d


def compress(x, thresh_db=-17.0, ratio=1.7, makeup=0.0):
    mono = x.mean(1)
    hop = SR // 100
    nf = len(mono) // hop
    e = (mono[:nf * hop].reshape(nf, hop).astype(np.float64) ** 2).mean(1)
    # 50 ms RMS window
    e = np.convolve(e, np.ones(5) / 5, "same")
    lvl = 10 * np.log10(e + 1e-12)
    over = np.maximum(lvl - thresh_db, 0)
    g = -over * (1 - 1 / ratio)
    # attack ~ 20ms, release ~ 250 ms (forward pass smoothing)
    ga, gr = np.exp(-1 / 2.0), np.exp(-1 / 25.0)
    s = np.zeros_like(g)
    prev = 0.0
    for i, v in enumerate(g):
        c = ga if v < prev else gr
        prev = c * prev + (1 - c) * v
        s[i] = prev
    gt = np.interp(np.arange(len(mono)), (np.arange(nf) + 0.5) * hop, s)
    return x * (10 ** ((gt + makeup) / 20))[:, None].astype(np.float32), s


def mix(cv, kick_times, send_ir, targets=None):
    n = cv.n
    T = dict(pad=-27.0, arp=-31.0, air=-39.0, bass=-26.0, kick=-29.0, clap=-37.0, shk=-47.0, hat=-46.0)
    FIXED = dict(riser=-26.0, impact=-17.0)   # peak dBFS (pre-master), not RMS-scaled
    if targets:
        T.update(targets)
    duck = duck_curve(n, kick_times, depth=0.22, tau=0.07).astype(np.float32)[:, None] if kick_times else np.float32(1.0)
    dry = np.zeros((n, 2), np.float32)
    send = np.zeros((n, 2), np.float32)

    def take(k):
        if k not in cv.s:
            return None
        v = cv.s.pop(k)
        if k in FIXED:
            return v * np.float32(10 ** (FIXED[k] / 20)) if np.abs(v).max() > 0 else None
        if np.abs(v).max() > 0:
            v = scale_to(v, T[k])
        else:
            return None
        return v

    x = take("pad")
    x = sos_f("low", 2300, 4, sos_f("high", 110, 2, x))
    dry += x * duck; send += np.float32(0.30) * x; del x
    x = take("arp")
    x = sos_f("high", 250, 2, sos_f("low", 3600, 2, x))
    d = int(0.75 * BEAT * SR)   # dotted-eighth ping-pong
    mono = x.mean(1)
    wl = np.zeros(n, np.float32); wr = np.zeros(n, np.float32)

    def sh(m, k, g, out):
        if k < n:
            out[k:] += np.float32(g) * m[:n - k]
    sh(mono, d, 0.4, wl); sh(mono, 3 * d, 0.14, wl)
    sh(mono, 2 * d, 0.28, wr); sh(mono, 4 * d, 0.09, wr)
    del mono
    dly = sos_f("high", 300, 2, sos_f("low", 2800, 2, np.stack([wl, wr], 1)))
    del wl, wr
    dry += (np.float32(0.85) * x + np.float32(0.6) * dly) * duck
    send += np.float32(0.28) * (x + dly)
    del x, dly
    x = take("air")
    if x is not None:
        x = sos_f("high", 300, 2, x); dry += x * duck; send += np.float32(0.5) * x; del x
    x = take("bass")
    if x is not None:
        x = sos_f("low", 450, 2, x); m = x.mean(1, keepdims=True); dry += m * duck; del x, m
    x = take("kick")
    if x is not None:
        dry += x; del x
    x = take("clap")
    if x is not None:
        dry += x; send += np.float32(0.22) * x; del x
    x = take("shk")
    if x is not None:
        dry += x; send += np.float32(0.1) * x; del x
    x = take("hat")
    if x is not None:
        dry += x; send += np.float32(0.05) * x; del x
    x = take("riser")
    if x is not None:
        dry += np.float32(0.8) * x; send += np.float32(0.35) * x; del x
    x = take("impact")
    if x is not None:
        dry += x; send += np.float32(0.25) * x; del x
    wet = reverb(send, send_ir)
    del send
    dry += wet
    return dry


SEC_DB = {"INTRO": (-5.0, -1.0), "A": (-0.5, -0.5), "B": (1.0, 1.0), "A2": (-0.3, 0.0), "BRK": (-4.0, -2.0),
          "B2": (1.0, 1.0), "C": (1.5, 1.5), "OUTRO": (-1.0, -5.0)}


def _measure(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    s = r[r.rindex("Summary:"):]
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", s)[0]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", s)[0])


def loudnorm_file(src, dst, I=-16.0, TP=-1.5, LRA=11):
    """static gain to I LUFS integrated, then a lookahead limiter (sample ceiling TP-0.5) so true peak <= TP; re-trim gain
    until the limited result sits at I (+-0.1 LU). Replaces ffmpeg loudnorm, which falls back to dynamic mode on transient-rich music."""
    cur, _ = _measure(src)
    g = I - cur
    ceil = 10 ** ((TP - 0.5) / 20)
    for it in range(5):
        af = f"volume={g:.3f}dB,alimiter=limit={ceil:.4f}:attack=2:release=40:asc=0:level=disabled"
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-af", af, "-ar", str(SR),
                        "-ac", "2", "-c:a", "pcm_s16le", dst], check=True)
        li, tp = _measure(dst)
        print(f"  {os.path.basename(dst)} it{it}: I={li} LUFS  TP={tp} dBTP  gain={g:.2f}", flush=True)
        if abs(li - I) <= 0.1 and tp <= TP:
            break
        g += (I - li)
    return dict(I=li, TP=tp)


def write_f32(path, x):
    wavfile.write(path, SR, x.astype(np.float32))




ARP16 = {  # chord-tone index per 16th step
    "P1": [0, 1, 2, 3, 2, 1, 2, 3, 0, 1, 2, 3, 2, 3, 2, 1],
    "P2": [0, 2, 1, 3, 2, 3, 1, 2, 0, 2, 1, 3, 3, 2, 1, 2],
    "P3": [3, 2, 1, 0, 1, 2, 3, 2, 3, 2, 1, 0, 1, 0, 1, 2],
}
ARP_VEL = [1.0, .5, .72, .52]            # accent on the beat, light on the 16th "e"/"a"


# ================================================================ v4 additions
def set_tempo(bpm):
    global BPM, BEAT, BAR, E8, S16
    BPM = bpm
    BEAT = 60.0 / bpm
    BAR = 4 * BEAT
    E8 = BEAT / 2
    S16 = BEAT / 4


CH["Bm7"] = ([47, 54, 59, 62, 66], [62, 66, 69, 74], 35)
CH["Dm"] = ([50, 57, 62, 65], [62, 65, 69, 74], 38)


def clock_tick(v, big=False):
    """dry clock tick: band-limited click + tiny wooden body; v alternates tick / tock pitch."""
    r = np.random.default_rng(900 + v)
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    f0 = 1250 if v % 2 == 0 else 980
    body = np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.012)
    nz = ss.sosfilt(ss.butter(2, [1800, 5200], btype="band", fs=SR, output="sos"), r.standard_normal(n)) * np.exp(-t / 0.004)
    y = body * 0.6 + nz * 0.5
    y *= (1 - np.exp(-t / 0.0004))
    y[-300:] *= np.linspace(1, 0, 300)
    return y


@lru_cache(maxsize=None)
def drone_wave(m, dur, seed):
    """dark low drone: detuned saws, filter opens slowly (crossfade between dark and brighter copy)."""
    f = float(mtof(m))
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for c in (-9, 0, 8):
        fq = f * 2 ** (c / 1200)
        y += ss.sawtooth(2 * np.pi * fq * t + c) / 3
    dark = ss.sosfilt(ss.butter(2, 220, "low", fs=SR, output="sos"), y)
    bright = ss.sosfilt(ss.butter(2, 900, "low", fs=SR, output="sos"), y)
    u = (t / dur) ** 1.5
    out = dark * (1 - u) + bright * u * 0.8
    out *= (1 + 0.12 * np.sin(2 * np.pi * 0.17 * t))
    na = int(1.2 * SR)
    out[:na] *= np.linspace(0, 1, na) ** 2
    return out


def cluster_wave(dur, seed):
    """unease cluster: minor 2nd / tritone sine tones with slow tremolo, fades in."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    r = np.random.default_rng(seed)
    out = np.zeros((n, 2))
    for k, m in enumerate((62, 63, 69, 68, 74)):   # D4 Eb4 A4 Ab4 D5
        f = float(mtof(m))
        trem = 0.55 + 0.45 * np.sin(2 * np.pi * r.uniform(0.2, 0.5) * t + r.uniform(0, 6))
        y = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)) * trem
        pan = -0.6 + 0.3 * k
        th = (pan + 1) * np.pi / 4
        out[:, 0] += y * np.cos(th)
        out[:, 1] += y * np.sin(th)
    env = (t / dur) ** 2.0
    return out * env[:, None] / 5


def glide_wave(dur):
    """slowly rising pitch glide (uneasy), sine + soft vibrato."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    u = t / dur
    f = 180 * (1500 / 180) ** (u ** 1.3)
    f = f * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.2 * np.sin(2 * ph)
    return y * u ** 2.5


def rev_swell(dur, seed=8):
    """noise swell, band 300-3500, quadratic rise (suck-in)."""
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros((n, 2))
    sos = ss.butter(2, [300, 3500], btype="band", fs=SR, output="sos")
    u = np.linspace(0, 1, n)
    for ch in range(2):
        out[:, ch] = ss.sosfilt(sos, r.standard_normal(n)) * u ** 2.5
    return out


def heart_wave():
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    f = 42 + 40 * np.exp(-t / 0.03)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - np.exp(-t / 0.003)) * np.exp(-t / 0.11)
    y[-300:] *= np.linspace(1, 0, 300)
    return y


def render_dark(pain_end, seed=21):
    """dark bus 0..pain_end, with a hard-gated suck-back SUCK s before pain_end (all energy incl. reverb tail)."""
    SUCK = 0.25
    gate_t = pain_end - SUCK
    n = int((pain_end + 0.5) * SR)
    cv = Canvas(n)
    rng = np.random.default_rng(seed)
    # drones: D1 + A1 (open 5th removed later -> bare D, then Ab tritone creeps in)
    cv.add("drone", 0.0, drone_wave(26, round(gate_t, 2), 1), 1.0, 0.0)
    cv.add("drone", 0.0, drone_wave(38, round(gate_t, 2), 2), 0.7, 0.0)
    if gate_t > 5:
        cv.add("drone", gate_t * 0.45, drone_wave(37, round(gate_t * 0.55, 2), 3), 0.45, 0.0)   # Db against D: grinding semitone
    cv.add("cluster", gate_t * 0.25, cluster_wave(gate_t * 0.75, 4), 1.0)
    cv.add("glide", gate_t * 0.3, np.stack([glide_wave(gate_t * 0.7)] * 2, 1), 1.0)
    cv.add("swell", gate_t - 5.0, rev_swell(5.0), 1.0)
    # clock: interval 0.62 -> 0.24 s
    t, k = 0.35, 0
    while t < gate_t - 0.03:
        u = min(1.0, t / gate_t)
        cv.add("tick", t, clock_tick(k), (0.35 + 0.65 * u) * (1.0 if k % 2 == 0 else 0.72), (0.25 if k % 2 == 0 else -0.25))
        t += 0.62 * (0.24 / 0.62) ** u
        k += 1
    # soft heartbeat lub-dub from 40 % on, getting denser
    t = gate_t * 0.4
    while t < gate_t - 0.3:
        u = t / gate_t
        cv.add("heart", t, heart_wave(), 0.6 + 0.5 * u)
        cv.add("heart", t + 0.2, heart_wave(), 0.4 + 0.4 * u)
        t += 1.5 - 0.7 * u
    # mix
    def sc(name, db):
        return scale_to(cv.s[name], db)
    ir = make_ir(3.4, pre=0.03, seed=17)
    dry = np.zeros((n, 2), np.float32)
    send = np.zeros((n, 2), np.float32)
    x = sc("drone", -27.0); x = sos_f("low", 900, 2, sos_f("high", 38, 2, x)); dry += x; send += 0.15 * x
    x = sc("cluster", -39.0); x = sos_f("high", 200, 2, sos_f("low", 2500, 2, x)); dry += x; send += 0.5 * x
    x = sc("glide", -43.0); x = sos_f("low", 2500, 2, x); dry += x; send += 0.4 * x
    x = cv.s["swell"]; x = x / (np.abs(x).max() + 1e-9) * 10 ** (-27 / 20); dry += x; send += 0.4 * x
    x = sc("tick", -43.0); dry += x; send += 0.18 * x
    x = sc("heart", -33.0); x = sos_f("low", 200, 2, x); dry += x.mean(1, keepdims=True) * np.ones((1, 2), np.float32)
    wet = reverb(send, ir)
    out = dry + wet
    # suck-back gate: 20 ms fade-out at gate_t, silence to pain_end (and beyond)
    g = np.ones(n, np.float32)
    i0 = int(gate_t * SR)
    fo = int(0.02 * SR)
    g[i0:i0 + fo] = np.linspace(1, 0, fo)
    g[i0 + fo:] = 0
    fi = int(0.4 * SR)
    g[:fi] *= np.linspace(0, 1, fi) ** 2
    return out * g[:, None]


# ---------------------------------------------------------------- groove plan
def snap_tempo(dur, lo=124.0, hi=128.0, pref=126.0):
    """choose integer number of bars N in the section so that BPM = 240 N / dur lies in [lo, hi] closest to pref."""
    best = None
    for N in range(1, 400):
        bpm = 240.0 * N / dur
        if lo <= bpm <= hi and (best is None or abs(bpm - pref) < abs(best[1] - pref)):
            best = (N, bpm)
    if best is None:                     # fall back: nearest-to-pref integer N, tempo may fall outside range
        N = max(1, round(pref * dur / 240.0))
        best = (N, 240.0 * N / dur)
    return best


LOOP1 = ["D", "A", "Bm", "G"]
LOOP2 = ["Bm", "G", "D", "A"]


def build_main(a):
    pe, te, os_, fh, length = a.pain_end, a.title_end, a.outro_start, a.final_hit, a.length
    N, bpm = snap_tempo(os_ - te)
    set_tempo(bpm)
    print(f"groove: {N} bars, {bpm:.3f} BPM, bar={BAR:.4f}s, beat={BEAT:.4f}s")
    cv = Canvas(int((length + 1) * SR))
    rng = np.random.default_rng(4)
    kt = []

    # ---------------- title lift: pe -> te (grid anchored backwards from te)
    cv.add("impact", pe, impact_wave(), 1.15)
    dur_t = te - pe
    seq = ["D", "Bm", "G", "A"]
    seg = dur_t / len(seq)
    for i, ch in enumerate(seq):
        pad_n, arp_t, bass_r = CH[ch]
        t0 = pe + i * seg
        pw = pad_wave(tuple(pad_n), round(seg + 0.1, 3), 0.04 if i == 0 else 0.25, 1.0, zlib.crc32(ch.encode()) % 97 + 5)
        cv.add("pad", t0 - 0.02, pw, 1.15 if i == 0 else 1.0)
        cv.add("pad", t0 - 0.02, pad_wave(tuple(m + 12 for m in pad_n[1:]), round(seg + 0.1, 3), 0.1, 1.0, zlib.crc32(ch.encode()) % 89 + 9), 0.45)
        cv.add("bass", t0, bass_wave(bass_r, round(seg - 0.1, 2), 1.6), 0.9)
    cv.add("air", pe, air_wave(78, round(dur_t, 2)), 1.0)
    cv.add("pad", pe, pad_wave(tuple(CH["Dadd"][0]), 0.1, 0.01, 0.1, 3), 0.0)
    # bell arpeggio in 8ths on the groove grid (back from te), bright
    k = 1
    ts = []
    while te - k * E8 > pe + 0.15:
        ts.append(te - k * E8)
        k += 1
    ts.sort()
    for j, t in enumerate(ts):
        ci = min(len(seq) - 1, int((t - pe) / seg))
        arp_t = CH[seq[ci]][1]
        m = arp_t[[0, 1, 2, 3, 2, 1][j % 6]] + (12 if (j // 6) % 2 else 0)
        cv.add("arp", t, pluck16_wave(int(min(m, 88)), 1.0), 0.8 + 0.12 * (j % 2), 0.5 * np.sin(j * 1.3))
    # soft light shaker/hat 8ths in 2nd half, no kick
    for t in ts:
        if t > pe + dur_t * 0.45:
            cv.add("hat", t + E8 / 2 * 0, hat_wave(int(rng.integers(0, 4))), 0.45, 0.3)
    # lead-in riser (last 1.5 s) + clap roll in the last beat
    cv.add("riser", te - 1.5, riser_wave(1.5, 5), 0.8)
    for i, v in enumerate((0.3, 0.45, 0.6, 0.85)):
        cv.add("clap", te - BEAT + i * S16, clap_wave(i % 3), v)

    # ---------------- groove: N bars from te
    for b in range(N):
        t0 = te + b * BAR
        loop = LOOP1 if b < 16 else LOOP2
        ch = loop[b % 4]
        if b % 8 == 7 and b >= 15:
            ch = "A"
        pad_n, arp_t, bass_r = CH[ch]
        inten = b / max(1, N - 1)
        fill = (b % 8 == 7)
        # impact on phrase starts
        if b == 0:
            cv.add("impact", t0, impact_wave(), 0.75)
            cv.add("clap", t0, clap_wave(0), 0.9)
        elif b % 8 == 0:
            cv.add("impact", t0, impact_wave(), 0.35 + 0.15 * inten)
        # pad
        cv.add("pad", t0 - 0.03, pad_wave(tuple(pad_n), round(BAR + 0.1, 3), 0.4, 1.0, zlib.crc32(ch.encode()) % 97), 0.6 + 0.5 * inten)
        # kick: four on the floor, last beat of fill drops (replaced by clap roll)
        for beat in range(4):
            if fill and beat == 3:
                continue
            cv.add("kick", t0 + beat * BEAT, kick_wave(), 0.9 if beat else 1.0)
            kt.append(t0 + beat * BEAT)
        # offbeat bass (8th offbeats) + octave pickup later on
        for stp in (2, 6, 10, 14):
            if fill and stp >= 14:
                continue
            cv.add("bass", t0 + stp * S16, bass_wave(bass_r, 0.2, 0.12), 0.8 + 0.06 * (stp == 2))
        if b >= 12 and not fill:
            cv.add("bass", t0 + 15 * S16, bass_wave(bass_r + 12, 0.1, 0.08), 0.45)
        # hats: offbeat open-ish 8ths always; 16ths after bar 16
        for i in (2, 6, 10, 14):
            cv.add("hat", t0 + i * S16 + rng.uniform(-.002, .002), hat_wave(int(rng.integers(0, 4))), 0.55 * rng.uniform(.85, 1), 0.3)
        if b >= 8:
            for i in (0, 1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 15):
                if b < 16 and i % 2 == 0 and i not in (0, 4, 8, 12):
                    continue
                v = [.3, .2, .0, .26][i % 4] if i % 4 != 2 else .0
                if v > 0:
                    cv.add("hat", t0 + i * S16 + rng.uniform(-.002, .002), hat_wave(int(rng.integers(0, 4))), v * rng.uniform(.85, 1),
                           0.35 * (1 if i % 8 < 4 else -1))
        # claps on 2 and 4 from bar 4 (soft), full from 8
        if b >= 4:
            cv_gain = 0.55 if b < 8 else 0.85
            for sl in (4, 12):
                if fill and sl == 12:
                    continue
                cv.add("clap", t0 + sl * S16 + rng.uniform(-.002, .002), clap_wave(int(rng.integers(0, 3))), cv_gain)
        if fill:
            for sl, v in ((12, .45), (13, .5), (14, .7), (15, .95)) if b % 16 == 7 else ((12, .4), (13, .4), (14, .6), (15, .75), (11, .3)):
                cv.add("clap", t0 + sl * S16, clap_wave(sl % 3), v)
            cv.add("riser", t0 + BAR * 0.5, riser_wave(round(BAR * 0.5, 3), 40 + b), 0.55)
        # arps: 8ths bars 0-3 (bright 0.5), 16ths from bar 4, pattern swap each 4 bars
        if b < 4:
            for i in range(0, 16, 2):
                ti = ARP16["P1"][i]
                cv.add("arp", t0 + i * S16, pluck16_wave(int(arp_t[ti]), 0.4), 0.6 * (1.0 if i % 4 == 0 else 0.7), np.sin(i * .7) * 0.4)
        else:
            pk = ["P1", "P2", "P3", "P2"][(b // 4) % 4]
            ml = 0.55 + 0.5 * inten
            for i in range(16):
                if fill and i >= 12:
                    continue
                ti = ARP16[pk][i]
                m = int(arp_t[ti])
                cv.add("arp", t0 + i * S16 + rng.uniform(-.002, .002), pluck16_wave(m, 0.5 + 0.5 * inten),
                       ARP_VEL[i % 4] * ml * rng.uniform(0.93, 1.0), np.sin(2 * np.pi * (b * 16 + i) / 13.0) * 0.45)
        # air layer from bar 12 every 2 bars
        if b >= 12 and b % 2 == 0:
            cv.add("air", t0, air_wave(int(arp_t[3]), round(BAR * 2, 2)), 0.9)

    # ---------------- anthem: os_ -> fh
    D = fh - os_
    cv.add("impact", os_, impact_wave(), 0.9)
    cv.add("clap", os_, clap_wave(1), 0.9)
    chords = ["G", "A", "Bm", "G", "A", "Bm", "A", "A"]
    nb = int(np.ceil(D / BAR))
    for b in range(nb):
        t0 = os_ + b * BAR
        if t0 >= fh - 0.3:
            break
        ch = chords[b]
        pad_n, arp_t, bass_r = CH[ch]
        u = b / max(1, nb - 1)
        seglen = min(BAR, fh - t0) + 0.1
        cv.add("pad", t0 - 0.03, pad_wave(tuple(pad_n), round(seglen, 3), 0.35, 1.0, zlib.crc32(ch.encode()) % 97 + 11), 1.0 + 0.45 * u)
        cv.add("pad", t0 - 0.03, pad_wave(tuple(m + 12 for m in pad_n), round(seglen, 3), 0.5, 1.0, zlib.crc32(ch.encode()) % 83 + 21), 0.7 + 0.5 * u)
        cv.add("pad", t0 - 0.03, pad_wave(tuple([pad_n[0] - 12, pad_n[1] - 12]), round(seglen, 3), 0.3, 1.0, zlib.crc32(ch.encode()) % 79 + 31), 0.5)
        cv.add("bass", t0, bass_wave(bass_r, round(min(BAR, fh - t0) - 0.25, 2), 1.5), 0.85)
        cv.add("air", t0, air_wave(int(arp_t[3]) + (12 if b >= 3 else 0), round(BAR, 2)), 0.8 + 0.3 * u)
        # kick on beats until final lead-in
        for beat in range(4):
            tk = t0 + beat * BEAT
            if tk < fh - 1.9 and b >= 0:
                cv.add("kick", tk, kick_wave(), 0.85)
                kt.append(tk)
        # 8th arps rising: octave shift up after bar 2
        for i in range(0, 16, 2):
            t = t0 + i * S16
            if t > fh - 0.35:
                break
            m = int(arp_t[ARP16["P3"][i]]) + (12 if b >= 3 and arp_t[ARP16["P3"][i]] < 76 else 0)
            cv.add("arp", t, pluck16_wave(min(m, 90), 0.9), (0.55 + 0.4 * u) * (1 if i % 4 == 0 else 0.75), np.sin(i * .7 + b) * 0.5)
        # clap backbeat after bar 1
        if b >= 1:
            for sl in (4, 12):
                if t0 + sl * S16 < fh - 1.9:
                    cv.add("clap", t0 + sl * S16, clap_wave(sl % 3), 0.7)
        for i in range(0, 16, 2):
            if t0 + i * S16 < fh - 0.4:
                cv.add("hat", t0 + i * S16 + S16 / 1e9, hat_wave(i % 4), 0.4 if i % 4 else 0.28, 0.3)
    # swell + riser into final hit + accelerating snare roll in last ~1.9 s
    cv.add("swell", fh - 4.0, swell_wave(4.0 - 0.13, 9, 2.4) * 0 + swell_wave(4.0 - 0.13, 9, 2.4), 1.0)
    cv.add("riser", fh - 4.0, riser_wave(4.0 - 0.12, 77), 1.0)
    t = fh - 1.9
    iv = 0.24
    j = 0
    while t < fh - 0.14:
        u = 1 - (fh - t) / 1.9
        cv.add("clap", t, clap_wave(j % 3), 0.35 + 0.65 * u)
        t += iv * (0.35 + 0.65 * (1 - u))
        j += 1
    # ---------------- final: chord + impact
    fdur = length - fh
    cv.add("impact", fh, impact_wave(), 1.3)
    cv.add("kick", fh, kick_wave(), 1.0); kt.append(fh)
    cv.add("clap", fh, clap_wave(2), 0.9)
    pn = CH["Dadd"][0]
    cv.add("pad", fh - 0.02, pad_wave(tuple(pn), round(fdur - 1.5, 2), 0.03, 1.5, 61), 1.35)
    cv.add("pad", fh - 0.02, pad_wave(tuple(m + 12 for m in pn), round(fdur - 1.5, 2), 0.05, 1.5, 62), 0.9)
    cv.add("pad", fh - 0.02, pad_wave((38, 45), round(fdur - 1.5, 2), 0.03, 1.5, 63), 0.7)
    cv.add("bass", fh, bass_wave(38, round(fdur - 1.5, 2), 3.0), 1.0)
    cv.add("air", fh, air_wave(78, round(fdur - 1.5, 2)), 1.1)
    for i, m in enumerate([86, 81, 78, 74, 69, 66, 62]):
        cv.add("arp", fh + 0.02 + i * E8, pluck16_wave(m, 0.7), 0.9 - 0.09 * i, 0.4 * (-1) ** i)
    return cv, kt, N, bpm


# ---------------------------------------------------------------- master
def master4(x, a):
    pe, te, os_, fh, length = a.pain_end, a.title_end, a.outro_start, a.final_hit, a.length
    n = len(x)
    pts = [(0, -3.0), (pe, 0.0), (te - 0.3, 0.5), (te + 0.3, -1.0), (te + (os_ - te) * 0.5, 0.8), (os_ - 0.3, 2.0),
           (os_ + 0.3, 0.8), (fh - 0.3, 2.5), (fh + 0.3, 1.5), (length, 0.0)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    g = (10 ** (np.interp(np.arange(n) / SR, xs, ys) / 20)).astype(np.float32)[:, None]
    x = x * g
    # pre-impact suck-back before final hit (0.14 s dip, 12 ms ramps)
    dip = np.ones(n, np.float32)
    i1 = int(fh * SR); i0 = i1 - int(0.14 * SR); rp = int(0.012 * SR)
    dip[i0:i1] = 0.04
    dip[i0 - rp:i0] = np.linspace(1, 0.04, rp)
    x = x * dip[:, None]
    x = sos_f("high", 32, 2, x)
    x = peaking(x, 2200, -4.0, 0.6)     # keep 1-4 kHz clear for narration
    x = peaking(x, 1200, -1.5, 0.8)
    x = peaking(x, 3400, -2.5, 0.8)
    x = peaking(x, 330, -1.5, 0.9)
    x = sos_f("low", 11000, 2, x)
    x, _ = compress(x)
    x = x[: int(length * SR)]
    fi = int(0.03 * SR)
    x[:fi] *= np.linspace(0, 1, fi)[:, None]
    nf = int(min(4.5, length - fh - 1.0) * SR)
    t = np.linspace(0, 1, nf)
    x[-nf:] *= (np.cos(t * np.pi / 2) ** 2)[:, None]
    return x


def loudnorm24(src, dst):
    return loudnorm_file(src, dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pain-end", type=float, default=13.6)
    ap.add_argument("--title-end", type=float, default=19.6)
    ap.add_argument("--outro-start", type=float, default=85.0)
    ap.add_argument("--final-hit", type=float, default=97.1)
    ap.add_argument("--length", type=float, default=105.0)
    ap.add_argument("--out", default="/home/claude/video/t4/bgm_v4.wav")
    ap.add_argument("--tmp", default="/tmp/claude-0/-home-claude/4a98c7fc-ad86-519e-b225-277215eac05a/scratchpad")
    a = ap.parse_args()
    assert 0 < a.pain_end < a.title_end < a.outro_start < a.final_hit < a.length - 3, "timings out of order"
    os.makedirs(a.tmp, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    dark = render_dark(a.pain_end)
    cv, kt, N, bpm = build_main(a)
    print("mixing ...", flush=True)
    y = mix(cv, kt, make_ir(2.6))
    del cv
    k = min(len(y), len(dark))
    y[:k] += dark[:k]
    y = master4(y, a)
    raw = os.path.join(a.tmp, "bgm4_raw.wav")
    write_f32(raw, y)
    js = loudnorm_file(raw, a.out)
    print("final:", js, "out:", a.out, f"bars={N} bpm={bpm:.3f}")
    json.dump(dict(bars=N, bpm=bpm, **vars(a)), open(os.path.join(a.tmp, "bgm4_meta.json"), "w"))


if __name__ == "__main__":
    main()
