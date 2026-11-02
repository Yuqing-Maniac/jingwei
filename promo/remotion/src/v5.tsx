import React from 'react';
import {AbsoluteFill, Img, spring, staticFile, useCurrentFrame} from 'remotion';
import {AMBER, BLUE, BRAND, Backdrop, Diagram, INK, SANS, Stage, TEAL, inout, lerp, prog} from './common';
import {Flash, Glitch, Impact, Sweep, TitleTxt, Wipe, kick, rnd, shakeXY, slam, snap} from './v3';
import {ICONS} from './iconlist';

// ============================================================ shared v4 kit
export const RED = '#FF4D5E';
const cl = (x: number) => Math.max(0, Math.min(1, x));
export const sp = (f: number, t: number, d = 12, s = 220, m = 0.6) => (f < t ? 0 : spring({frame: f - t, fps: 30, config: {damping: d, stiffness: s, mass: m}}));
const lin = (t: number) => t;

export const Particles: React.FC<{f: number; n?: number; seed?: number; color?: string; op?: number; vy?: number}> = ({f, n = 60, seed = 1, color = '#9FD3FF', op = 1, vy = 0.6}) => (
  <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, opacity: op, pointerEvents: 'none'}}>
    {Array.from({length: n}).map((_, i) => {
      const r = rnd(i * 7 + seed);
      const x = ((rnd(i * 3 + seed * 11) * 1920 + f * (rnd(i + seed) - 0.5) * 0.8) % 1920 + 1920) % 1920;
      const v = 0.3 + rnd(i * 5 + seed) * vy * 2;
      const y = ((rnd(i * 13 + seed) * 1180 - f * v) % 1180 + 1180) % 1180 - 50;
      const tw = 0.4 + 0.6 * Math.abs(Math.sin(f / 14 + i));
      return <circle key={i} cx={x} cy={y} r={0.8 + r * 2.2} fill={color} opacity={(0.25 + 0.5 * r) * tw} />;
    })}
  </svg>
);

export const Scan: React.FC<{f: number; op?: number; tint?: string}> = ({f, op = 1, tint = '120,190,255'}) => (
  <>
    <AbsoluteFill style={{background: `repeating-linear-gradient(180deg, rgba(${tint},0.045) 0px, rgba(${tint},0.045) 1px, transparent 1px, transparent 4px)`, opacity: op, pointerEvents: 'none'}} />
    <div style={{position: 'absolute', left: 0, right: 0, top: ((f * 11) % 1500) - 260, height: 180, opacity: op, pointerEvents: 'none',
      background: `linear-gradient(180deg, rgba(${tint},0) 0%, rgba(${tint},0.02) 75%, rgba(${tint},0.07) 100%)`}} />
  </>
);

// kinetic characters: each glyph springs in
export const KChars: React.FC<{text: string; f: number; t: number; size: number; stagger?: number; color?: string | ((i: number) => string);
  family?: string; weight?: number; ls?: string; glow?: string; mode?: 'up' | 'zoom' | 'drop'}> =
  ({text, f, t, size, stagger = 2, color = '#EEF6FF', family = BRAND, weight = 400, ls = '0.06em', glow = 'rgba(76,168,255,0.55)', mode = 'up'}) => (
    <div style={{display: 'flex', fontFamily: family, fontSize: size, fontWeight: weight, letterSpacing: ls, whiteSpace: 'pre', lineHeight: 1.15}}>
      {Array.from(text).map((ch, i) => {
        const t0 = t + i * stagger;
        const s = sp(f, t0, 11, 280, 0.55);
        const op = cl((f - t0 + 1) / 3);
        const c = typeof color === 'function' ? color(i) : color;
        const tr = mode === 'zoom' ? `scale(${1 + (1 - s) * 1.8})` : mode === 'drop' ? `translateY(${(1 - s) * -120}px) rotate(${(1 - s) * 14}deg)` : `translateY(${(1 - s) * 70}px) rotate(${(1 - s) * -8}deg) scale(${1 + (1 - s) * 0.25})`;
        return <span key={i} style={{display: 'inline-block', color: c, opacity: op, transform: tr, textShadow: `0 0 18px ${glow}, 0 0 2px rgba(255,255,255,0.4)`}}>{ch}</span>;
      })}
    </div>
  );

const Streaks: React.FC<{f: number; a: number; b: number; dir?: number; color?: string; n?: number}> = ({f, a, b, dir = 1, color = BLUE, n = 18}) => {
  const p = prog(f, a, b, lin);
  if (p <= 0 || p >= 1) return null;
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      {Array.from({length: n}).map((_, i) => {
        const y = 120 + rnd(i * 3.3) * 820, L = 200 + rnd(i * 1.7) * 500;
        const x = dir > 0 ? -600 + p * (2600 + rnd(i) * 600) : 2520 - p * (2600 + rnd(i) * 600);
        return <line key={i} x1={x} y1={y} x2={x - dir * L} y2={y} stroke={i % 4 === 0 ? TEAL : color} strokeWidth={1.5 + rnd(i * 9) * 2.5} opacity={0.5 * Math.sin(p * Math.PI)} strokeLinecap="round" />;
      })}
    </svg>
  );
};

// CRT on (open from a line) / off
const CRT: React.FC<{f: number; a: number; b: number; mode: 'on' | 'off'; children: React.ReactNode}> = ({f, a, b, mode, children}) => {
  let p = prog(f, a, b, inout);
  if (mode === 'off') p = 1 - p;
  const sy = Math.max(0.004, p < 0.5 ? p * 2 * 0.02 + 0.002 : 0.02 + (p - 0.5) * 2 * 0.98);
  const sx = p < 0.5 ? Math.max(0.02, p * 2) : 1;
  const active = (mode === 'on' && f < b) || (mode === 'off' && f >= a);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <AbsoluteFill style={{transform: active ? `scale(${sx},${sy})` : undefined, filter: active && p < 0.9 ? `brightness(${1 + (1 - p) * 3})` : undefined}}>{children}</AbsoluteFill>
      {active && p > 0 && p < 1 && (
        <div style={{position: 'absolute', left: 960 - 960 * sx, width: 1920 * sx, top: 538, height: 4, background: '#fff', boxShadow: `0 0 30px ${BLUE}, 0 0 60px ${BLUE}`, opacity: 1 - p}} />
      )}
    </AbsoluteFill>
  );
};

const Badge: React.FC<{text: string; size?: number; color?: string; fill?: string}> = ({text, size = 34, color = BLUE, fill}) => (
  <div style={{fontFamily: SANS, fontWeight: 700, fontSize: size, letterSpacing: '0.04em', color: fill ? '#071226' : color, padding: `${size * 0.12}px ${size * 0.42}px`,
    border: `2.5px solid ${color}`, borderRadius: size * 0.28, background: fill ?? 'rgba(10,26,54,0.85)', boxShadow: `0 0 22px ${color}88`, lineHeight: 1.1, whiteSpace: 'pre'}}>{text}</div>
);

// ============================================================ 1. PAIN
const PAIN_T = {q1: 20, q2: 66, misalign: 115, net: 148, layer: 184, shuffle1: 202, shuffle2: 220, done: 261, stamp: 282, proj: 302, wipe: 334, slam: 345, gl: 378, off: 394};
const COLX = [470, 790, 1110, 1430];
const ROWY = [330, 540, 750];
const BOXL = ['感知节点', '数据链路', '指挥控制', '任务规划', '态势显示', '情报处理', '火力协同', '综合保障', '无人机', '无人艇', '地面站', '任务载荷'];
type BoxState = {x: number; y: number; r: number; w: number};
const messy = (slot: number, seed: number): BoxState => ({
  x: COLX[slot % 4] + (rnd(slot * 3 + seed) - 0.5) * 90,
  y: ROWY[Math.floor(slot / 4)] + (rnd(slot * 5 + seed * 7) - 0.5) * 70,
  r: (rnd(slot * 11 + seed * 3) - 0.5) * 12,
  w: 170 + rnd(slot * 13 + seed) * 90,
});
const PERM1 = [5, 0, 7, 2, 9, 11, 1, 3, 10, 4, 6, 8];
const PERM2 = [3, 8, 0, 10, 1, 6, 11, 5, 2, 7, 9, 4];
const boxAt = (f: number, i: number): BoxState & {s: number} => {
  const A = messy(i, 1), B = messy(PERM1[i], 2), C = messy(PERM2[i], 3);
  const s1 = sp(f, PAIN_T.shuffle1 + i * 0.7, 10, 180, 0.7), s2 = sp(f, PAIN_T.shuffle2 + (11 - i) * 0.6, 10, 180, 0.7);
  const s = sp(f, 30 + i * 6.5, 9, 170, 0.7);
  const wid = Math.floor(i / 4) === 1 ? 70 * sp(f, PAIN_T.layer + 4 + (i % 4) * 2, 10, 200, 0.6) : 0;
  return {
    x: A.x + (B.x - A.x) * s1 + (C.x - B.x) * s2,
    y: A.y + (B.y - A.y) * s1 + (C.y - B.y) * s2 - (1 - s) * 300,
    r: A.r + (B.r - A.r) * s1 + (C.r - B.r) * s2 + (1 - s) * 25,
    w: A.w + (B.w - A.w) * s1 + (C.w - B.w) * s2 + wid,
    s,
  };
};
const WIRES = Array.from({length: 24}).map((_, k) => {
  const a = Math.floor(rnd(k * 2.7 + 1) * 12);
  let b = Math.floor(rnd(k * 4.1 + 5) * 12);
  if (b === a) b = (a + 5) % 12;
  return {a, b, c1: [(rnd(k * 6.1) - 0.5) * 900, (rnd(k * 7.3) - 0.5) * 600], c2: [(rnd(k * 8.9) - 0.5) * 900, (rnd(k * 9.7) - 0.5) * 600], red: k % 3 === 0};
});
// virtual "elapsed" seconds on the racing timer
const timerSec = (f: number) => {
  if (f >= PAIN_T.wipe + 6) return 0;
  const K: [number, number][] = [[0, 0], [20, 40], [66, 900], [100, 2700], [148, 3 * 3600], [202, 7 * 3600], [246, 18 * 3600], [282, 37 * 3600 + 42 * 60 + 15]];
  if (f >= 282) return K[K.length - 1][1];
  for (let i = 1; i < K.length; i++) if (f < K[i][0]) { const [f0, v0] = K[i - 1], [f1, v1] = K[i]; return v0 + (v1 - v0) * ((f - f0) / (f1 - f0)); }
  return 0;
};
const hms = (s: number) => { s = Math.floor(s); const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60; return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(x).padStart(2, '0')}`; };

const TAGS: [number, string][] = [[115, '框对不齐'], [148, '线绕成网'], [184, '改一层'], [202, '就要重排整页'], [261, '好不容易画完'], [302, '换个项目']];

export const PainV5: React.FC = () => {
  const f = useCurrentFrame();
  const T = PAIN_T;
  const [sx, sy] = shakeXY(f, [T.q1, T.q2, T.misalign, T.net, T.shuffle1, T.shuffle1 + 4, T.shuffle2, T.shuffle2 + 4, T.slam, T.slam + 3], 10);
  const cam = 1.02 + 0.06 * prog(f, 0, 408, lin) + 0.03 * kick(f, T.shuffle1, 14) + 0.03 * kick(f, T.shuffle2, 14) + 0.05 * kick(f, T.slam, 14);
  const rot = 0.6 * Math.sin(f / 50) + 1.2 * kick(f, T.shuffle1, 18) - 1.2 * kick(f, T.shuffle2, 18);
  const qDim = 1 - prog(f, 100, 114);
  const qOut = prog(f, 98, 112, inout);
  const wipeP = prog(f, T.wipe, T.wipe + 16, inout);
  const barX = 200 + wipeP * 1560;
  const redAmt = 0.08 + 0.18 * prog(f, T.misalign, T.shuffle1) + 0.25 * kick(f, T.shuffle1, 20) + 0.25 * kick(f, T.shuffle2, 20) + 0.3 * prog(f, T.wipe, T.slam);
  const sec = timerSec(f);
  const resetBlink = f >= T.wipe + 6 ? (Math.floor((f - T.wipe) / 6) % 2 === 0 ? 1 : 0.25) : 1;
  const gEnd = prog(f, T.gl, T.off, lin);
  const pageOp = sp(f, 2, 14, 160, 0.8);
  const boxes = BOXL.map((_, i) => boxAt(f, i));
  const done = f >= T.stamp;
  const projFlip = prog(f, T.proj, T.proj + 8, lin);
  const projName = projFlip < 0.5 ? '边海防无人化巡逻体系' : '海岛无人值守监视系统';
  const verN = f < T.shuffle1 ? 1 : f < T.shuffle2 ? 4 : f < T.proj ? 9 : 1;

  const content = (
    <AbsoluteFill>
      <div style={{position: 'absolute', inset: 0, transform: `translate(${sx}px,${sy}px) scale(${cam}) rotate(${rot}deg)`, transformOrigin: '50% 48%'}}>
        <Backdrop glow={0.4} glowY={520} />
        <AbsoluteFill style={{background: `radial-gradient(ellipse 70% 65% at 50% 50%, transparent 40%, rgba(255,40,60,${redAmt}) 100%)`}} />
        {/* the page */}
        <div style={{position: 'absolute', left: 230, top: 150, width: 1460, height: 760, borderRadius: 14, opacity: pageOp, transform: `scale(${0.9 + 0.1 * pageOp})`,
          background: 'linear-gradient(180deg, rgba(20,40,74,0.92), rgba(12,26,52,0.92))', border: `1.5px solid rgba(140,190,255,0.35)`, boxShadow: '0 30px 80px rgba(0,0,0,0.6)',
          backgroundImage: 'linear-gradient(rgba(76,168,255,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(76,168,255,0.06) 1px, transparent 1px)', backgroundSize: '24px 24px'}}>
          <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 54, borderBottom: '1px solid rgba(140,190,255,0.25)', background: 'rgba(8,20,42,0.7)', borderRadius: '14px 14px 0 0',
            display: 'flex', alignItems: 'center', padding: '0 24px', gap: 18, fontFamily: SANS, fontSize: 24, color: '#BFD6F2'}}>
            {[RED, AMBER, TEAL].map((c, i) => <div key={i} style={{width: 13, height: 13, borderRadius: 7, background: c, opacity: 0.8}} />)}
            <div style={{marginLeft: 14, transform: `scaleY(${Math.abs(1 - 2 * projFlip)})`, color: projFlip >= 0.5 ? '#FFE2A8' : '#BFD6F2'}}>{`项目：${projName}`}</div>
            <div style={{marginLeft: 'auto', fontSize: 22, color: verN > 1 ? '#FF9AA4' : '#8FB4DC'}}>{`体系架构图 · 第 ${verN} 版`}</div>
          </div>
        </div>
        {/* diagram content (clipped by erase wipe) */}
        <div style={{position: 'absolute', inset: 0, clipPath: f >= T.wipe ? `inset(0 0 0 ${barX}px)` : undefined}}>
          <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
            {/* misalignment guides */}
            {(() => {
              const p = prog(f, T.misalign, T.misalign + 8) * (1 - prog(f, T.layer, T.layer + 10));
              if (p <= 0) return null;
              return boxes.map((b, i) => (
                <g key={i} opacity={p}>
                  <line x1={b.x - 150} y1={b.y - 40} x2={b.x + 150} y2={b.y - 40} stroke={RED} strokeWidth={1.6} strokeDasharray="7 6" />
                  {i % 4 !== 3 && <text x={b.x + 120} y={b.y - 48} fill={RED} fontSize={18} fontFamily={SANS} fontWeight={700}>{`Δ${Math.round(3 + rnd(i) * 19)}px`}</text>}
                </g>
              ));
            })()}
            {/* layer change band */}
            {f >= T.layer && f < T.shuffle2 + 16 && (
              <g opacity={(0.55 + 0.45 * (Math.floor((f - T.layer) / 4) % 2)) * (1 - prog(f, T.shuffle2, T.shuffle2 + 16))}>
                <rect x={250} y={ROWY[1] - 78} width={1420} height={156} fill={RED} fillOpacity={0.12} stroke={RED} strokeWidth={2} strokeDasharray="12 8" rx={8} />
                <text x={1650} y={ROWY[1] - 88} textAnchor="end" fill={RED} fontSize={24} fontFamily={SANS} fontWeight={700}>第二层 · 修改</text>
              </g>
            )}
            {/* tangled wires */}
            {WIRES.map((w, k) => {
              const p = prog(f, T.net - 3 + k * 1.4, T.net + 11 + k * 1.4, Easing2);
              if (p <= 0) return null;
              const A = boxes[w.a], B = boxes[w.b];
              const ax = A.x + A.w / 2, ay = A.y, bx = B.x - B.w / 2, by = B.y;
              const d = `M${ax} ${ay} C${ax + w.c1[0]} ${ay + w.c1[1]} ${bx + w.c2[0]} ${by + w.c2[1]} ${bx} ${by}`;
              const c = w.red ? RED : '#7FBFFF';
              return (
                <g key={k}>
                  <path d={d} fill="none" stroke={c} strokeOpacity={0.18} strokeWidth={7} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
                  <path d={d} fill="none" stroke={c} strokeOpacity={w.red ? 0.85 : 0.7} strokeWidth={2} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
                </g>
              );
            })}
            {/* boxes */}
            {boxes.map((b, i) => {
              if (b.s <= 0.001) return null;
              const hot = f >= T.layer && f < T.shuffle2 + 10 && Math.floor(i / 4) === 1;
              const c = hot ? RED : i % 2 ? TEAL : BLUE;
              return (
                <g key={i} transform={`translate(${b.x},${b.y}) rotate(${b.r})`} opacity={cl(b.s * 1.5)}>
                  <rect x={-b.w / 2} y={-38} width={b.w} height={76} rx={8} fill="#0B1D3C" stroke={c} strokeWidth={2} />
                  <rect x={-b.w / 2} y={-24} width={4} height={48} fill={c} />
                  <text x={0} y={9} textAnchor="middle" fontSize={25} fontWeight={500} fill="#E6F1FF" fontFamily={SANS}>{BOXL[i]}</text>
                </g>
              );
            })}
          </svg>
        </div>
        {/* erase bar */}
        {f >= T.wipe && wipeP < 1 && (
          <div style={{position: 'absolute', left: barX - 3, top: 140, width: 6, height: 780, background: '#fff', boxShadow: `0 0 24px ${RED}, 0 0 60px ${RED}`}} />
        )}
        {/* 完成 stamp */}
        {done && f < T.wipe && (
          <div style={{position: 'absolute', left: 1440, top: 250, transform: `rotate(-12deg) scale(${1 + (1 - sp(f, T.stamp, 9, 260, 0.6)) * 1.6})`, opacity: cl((f - T.stamp + 1) / 3) * (1 - prog(f, T.proj, T.proj + 10)),
            fontFamily: BRAND, fontSize: 64, color: AMBER, border: `5px solid ${AMBER}`, borderRadius: 12, padding: '2px 22px', letterSpacing: '0.1em', boxShadow: `0 0 26px ${AMBER}66`, background: 'rgba(40,24,6,0.55)'}}>
            画完了
          </div>
        )}
      </div>

      {/* HUD: timer (top-right, not shaken) */}
      <div style={{position: 'absolute', right: 70, top: 40, display: 'flex', alignItems: 'center', gap: 18, opacity: prog(f, 4, 14) * resetBlink}}>
        <svg width={64} height={64}>
          <circle cx={32} cy={32} r={27} fill="none" stroke={sec > 3600 ? RED : BLUE} strokeWidth={3.5} />
          <line x1={32} y1={32} x2={32 + 20 * Math.sin(sec / 600)} y2={32 - 20 * Math.cos(sec / 600)} stroke="#fff" strokeWidth={3} strokeLinecap="round" />
          <line x1={32} y1={32} x2={32 + 13 * Math.sin(sec / 7200 * Math.PI)} y2={32 - 13 * Math.cos(sec / 7200 * Math.PI)} stroke={sec > 3600 ? RED : BLUE} strokeWidth={4} strokeLinecap="round" />
        </svg>
        <div>
          <div style={{fontFamily: SANS, fontSize: 20, letterSpacing: '0.3em', color: '#8FB4DC'}}>已耗时</div>
          <div style={{fontFamily: SANS, fontWeight: 700, fontSize: 54, lineHeight: 1, fontVariantNumeric: 'tabular-nums', color: sec > 3600 || f >= T.wipe ? '#FF6B78' : '#EAF4FF',
            textShadow: `0 0 18px ${sec > 3600 || f >= T.wipe ? RED : BLUE}`, transform: `scale(${1 + 0.12 * kick(f, T.stamp, 10)})`, transformOrigin: 'left center'}}>{hms(sec)}</div>
        </div>
      </div>

      {/* keyword tags (top-left) */}
      {TAGS.map(([t, txt], i) => {
        const next = i + 1 < TAGS.length ? TAGS[i + 1][0] : T.wipe;
        if (f < t || f >= next + 6) return null;
        const s = sp(f, t, 11, 300, 0.55);
        const out = prog(f, next, next + 6, lin);
        return (
          <div key={i} style={{position: 'absolute', left: 70, top: 44, display: 'flex', alignItems: 'center', gap: 16, transform: `translateX(${(1 - s) * -260}px) translateY(${-out * 40}px)`, opacity: (1 - out) * cl((f - t + 1) / 3)}}>
            <div style={{width: 10, height: 66, background: RED, boxShadow: `0 0 16px ${RED}`}} />
            <KChars text={txt} f={f} t={t} size={60} stagger={1.5} glow="rgba(255,77,94,0.6)" />
          </div>
        );
      })}

      {/* opening question */}
      {f < 114 && (
        <>
          <AbsoluteFill style={{background: `rgba(3,8,18,${0.62 * qDim})`}} />
          <AbsoluteFill style={{alignItems: 'center', transform: `translateY(${-qOut * 120}px) scale(${1 - qOut * 0.15})`, opacity: 1 - qOut}}>
            <div style={{position: 'absolute', top: 330}}>
              <KChars text="一张体系架构图" f={f} t={T.q1} size={124} stagger={2.6} mode="zoom" />
            </div>
            <div style={{position: 'absolute', top: 520, display: 'flex', alignItems: 'center'}}>
              <KChars text="要画多久" f={f} t={T.q2} size={168} stagger={2.6} mode="drop" color="#FFFFFF" />
              <div style={{fontFamily: BRAND, fontSize: 200, color: RED, marginLeft: 10, opacity: cl((f - T.q2 - 11) / 2),
                transform: `scale(${(1 + (1 - sp(f, T.q2 + 11, 8, 300, 0.5)) * 2) * (1 + 0.06 * Math.sin(f / 3))}) rotate(${8 * Math.sin(f / 5)}deg)`, textShadow: `0 0 30px ${RED}`}}>？</div>
            </div>
          </AbsoluteFill>
        </>
      )}

      {/* 从头再来 */}
      {f >= T.slam && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
          <div style={{transform: `translateY(-40px) scale(${1 + (1 - slam(f, T.slam)) * 1.2})`, opacity: cl((f - T.slam + 1) / 2)}}>
            <Glitch f={f} g={Math.max(kick(f, T.slam, 10), gEnd, f % 37 < 2 ? 0.4 : 0)}>
              {(tint) => (
                <div style={{fontFamily: BRAND, fontSize: 250, letterSpacing: '0.06em', paddingLeft: '0.06em', lineHeight: 1.1, whiteSpace: 'pre',
                  ...(tint ? {color: tint} : {color: 'transparent', backgroundImage: 'linear-gradient(180deg,#FFFFFF 10%,#FFD3D8 55%,#FF4D5E 100%)', WebkitBackgroundClip: 'text', backgroundClip: 'text',
                    filter: 'drop-shadow(0 0 30px rgba(255,77,94,0.7))'})}}>从头再来</div>
              )}
            </Glitch>
          </div>
        </AbsoluteFill>
      )}
      <Impact f={f} t={T.slam} cx={960} cy={500} big={1} />
      <Flash f={f} t={T.slam} peak={0.55} dur={8} color="#FFD8DC" />
      <Flash f={f} t={T.shuffle1} peak={0.18} dur={5} color="#FF8090" />
      <Flash f={f} t={T.shuffle2} peak={0.18} dur={5} color="#FF8090" />
      <Particles f={f} n={40} seed={3} color="#FF9AA4" op={0.5 + 0.5 * prog(f, T.wipe, T.slam)} />
      <Scan f={f} op={0.8} tint="255,140,150" />
      {/* glitch bars at end */}
      {gEnd > 0 && Array.from({length: 7}).map((_, i) => {
        const y = rnd(f * 3 + i * 17) * 1080, h = 6 + rnd(f * 5 + i) * 50;
        return <div key={i} style={{position: 'absolute', left: 0, right: 0, top: y, height: h, background: i % 2 ? 'rgba(255,77,94,0.35)' : 'rgba(76,168,255,0.3)', transform: `translateX(${(rnd(f + i) - 0.5) * 200 * gEnd}px)`, opacity: gEnd}} />;
      })}
    </AbsoluteFill>
  );
  return (
    <Stage>
      <CRT f={f} a={T.off} b={T.off + 10} mode="off">{content}</CRT>
      {f >= T.off + 10 && <AbsoluteFill style={{background: '#000'}} />}
      <Flash f={f} t={0} peak={0.5} dur={6} />
    </Stage>
  );
};
const Easing2 = (t: number) => 1 - Math.pow(1 - t, 2);

// ============================================================ 2. TITLE
const TT = {title: 24, ver: 40, tag1: 60, tag2: 88, sweep: 120};
const VerBadge: React.FC<{f: number; t: number; size?: number; v?: string}> = ({f, t, size = 54, v = 'v3.2'}) => {
  const s = sp(f, t, 9, 300, 0.5);
  return (
    <div style={{opacity: cl((f - t + 1) / 2), transform: `scale(${1 + (1 - s) * 2}) rotate(${(1 - s) * -20}deg)`}}>
      <div style={{fontFamily: BRAND, fontSize: size, color: '#071226', background: `linear-gradient(135deg, #FFD27A, ${AMBER})`, padding: `0 ${size * 0.3}px`, borderRadius: size * 0.22,
        boxShadow: `0 0 ${20 + 40 * kick(f, t, 12)}px ${AMBER}`, lineHeight: 1.25, letterSpacing: '0.02em'}}>{v}</div>
    </div>
  );
};

export const TitleV5: React.FC = () => {
  const f = useCurrentFrame();
  const [sx, sy] = shakeXY(f, [TT.title, TT.ver], 10);
  const cam = 1.12 - 0.12 * prog(f, 0, 40) + 0.05 * prog(f, 40, 180, lin) + 0.04 * kick(f, TT.title, 12);
  const ps = slam(f, TT.title);
  const g = Math.max(kick(f, TT.title, 9), prog(f, 172, 180, lin) * 0.5);
  const guideP = prog(f, 8, 22, lin);
  const lineP = prog(f, TT.tag1 - 4, TT.tag1 + 14);
  return (
    <Stage>
      <CRT f={f} a={0} b={9} mode="on">
        <AbsoluteFill style={{transform: `translate(${sx}px,${sy}px) scale(${cam})`, transformOrigin: '50% 46%'}}>
          <Backdrop glow={prog(f, TT.title - 4, TT.title + 20)} glowY={440} />
          <div style={{position: 'absolute', inset: 0, opacity: 1 - 0.62 * prog(f, TT.title - 2, TT.title + 14), transform: 'scale(0.86)', transformOrigin: '50% 50%'}}>
            <Diagram start={1} speed={2.6} pulseStart={20} />
            {/* snap / alignment guides — the tidy contrast */}
            <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
              {[185, 895].map((y, i) => guideP > 0 && guideP < 1 && (
                <line key={i} x1={0} y1={y} x2={1920 * guideP} y2={y} stroke={TEAL} strokeWidth={2} strokeDasharray="10 8" opacity={Math.sin(guideP * Math.PI)} />
              ))}
              {[250, 620, 960, 1300, 1670].map((x, i) => guideP > 0 && guideP < 1 && (
                <line key={i} x1={x} y1={0} x2={x} y2={1080 * guideP} stroke={BLUE} strokeWidth={1.5} strokeDasharray="10 8" opacity={0.8 * Math.sin(guideP * Math.PI)} />
              ))}
            </svg>
          </div>
          <Particles f={f} n={50} seed={7} op={0.7} />
          <AbsoluteFill style={{alignItems: 'center'}}>
            {f >= TT.title && (
              <div style={{position: 'absolute', top: 420, transform: `translateY(-50%) scale(${1 + (1 - ps) * 1.1})`, opacity: cl((f - TT.title + 1) / 2)}}>
                <div style={{display: 'flex', alignItems: 'center', gap: 50}}>
                  <Img src={staticFile('logo.svg')} style={{width: 180, height: 180, filter: 'drop-shadow(0 10px 30px rgba(10,40,90,0.8)) drop-shadow(0 0 24px rgba(76,168,255,0.45))'}} />
                  <div style={{position: 'relative'}}>
                    <Glitch f={f} g={g}>{(tint) => <TitleTxt text="经纬织图" size={204} tint={tint} ls="0.08em" />}</Glitch>
                    <Sweep text="经纬织图" size={204} p={prog(f, TT.sweep, TT.sweep + 26, lin)} ls="0.08em" />
                    <div style={{position: 'absolute', right: -150, top: -18}}><VerBadge f={f} t={TT.ver} /></div>
                  </div>
                </div>
              </div>
            )}
            <div style={{position: 'absolute', top: 640, left: 0, right: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 6, transform: 'translateY(-50%)'}}>
              {f >= TT.tag1 && <KChars text="纵横经纬，" f={f} t={TT.tag1} size={70} stagger={2.2} family={SANS} weight={500} color="#DCEBFF" ls="0.12em" />}
              {f >= TT.tag2 && <KChars text="织网成图" f={f} t={TT.tag2} size={70} stagger={2.2} family={SANS} weight={700} color="#8FF0E6" ls="0.12em" glow="rgba(43,212,196,0.6)" />}
            </div>
            <div style={{position: 'absolute', top: 716, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
              <div style={{width: 900 * lineP, height: 3, background: `linear-gradient(90deg, transparent, ${BLUE}, ${TEAL}, transparent)`, boxShadow: `0 0 14px ${BLUE}`}} />
            </div>
          </AbsoluteFill>
          <Impact f={f} t={TT.title} cx={960} cy={420} big={1.1} />
          <Impact f={f} t={TT.ver} cx={1440} cy={330} n={10} r0={40} big={0.3} />
          <Streaks f={f} a={TT.title - 2} b={TT.title + 12} />
        </AbsoluteFill>
        <Scan f={f} op={0.6} />
      </CRT>
      <Flash f={f} t={TT.title} peak={0.8} dur={9} color="#DFF1FF" />
      <Flash f={f} t={TT.tag2} peak={0.12} dur={5} />
    </Stage>
  );
};

// ============================================================ 3. STING
export type StingV5Props = {num: string; title: string; sub?: string; isNew?: boolean; total?: number};
const gradTxt = (a: string, b: string): React.CSSProperties => ({color: 'transparent', backgroundImage: `linear-gradient(180deg, ${a} 5%, ${b} 100%)`, WebkitBackgroundClip: 'text', backgroundClip: 'text'});

export const StingV5: React.FC<StingV5Props> = ({num, title, sub, isNew, total = 6}) => {
  const f = useCurrentFrame();
  const idx = parseInt(num, 10);
  const [sx, sy] = shakeXY(f, [3, 10], 9);
  const sN = slam(f, 2);
  const g = Math.max(f < 6 ? 0.8 * (1 - f / 6) : 0, prog(f, 27, 32, lin) * 0.9 * (f < 33 ? 1 : 0), kick(f, 3, 5) * 0.6);
  const len = Array.from(title).length;
  const tSize = len <= 4 ? 176 : len <= 5 ? 156 : len <= 7 ? 130 : 112;
  const lineP = prog(f, 3, 12);
  const cam = 1 + 0.07 * prog(f, 0, 39, lin) + 0.03 * kick(f, 3, 8);
  const accent = isNew ? AMBER : BLUE;
  const Num = (tint?: string) => (
    <div style={{fontFamily: BRAND, fontSize: 400, lineHeight: 1, letterSpacing: '0.02em', ...(tint ? {color: tint} : gradTxt('#FFFFFF', isNew ? '#F2A33A' : '#3F9FF2')),
      ...(tint ? {} : {filter: `drop-shadow(0 0 30px ${isNew ? 'rgba(242,163,58,0.55)' : 'rgba(76,168,255,0.6)'})`})}}>{num}</div>
  );
  return (
    <Stage>
      <div style={{position: 'absolute', inset: 0, transform: `translate(${sx}px,${sy}px) scale(${cam})`}}>
        <Backdrop glow={0.8} glowY={500} />
        <Particles f={f + idx * 40} n={45} seed={idx * 5} op={0.8} vy={1.4} />
        <Streaks f={f} a={0} b={14} dir={-1} color={accent} n={22} />
        <AbsoluteFill>
          <div style={{position: 'absolute', left: 150, top: 160, display: 'flex', alignItems: 'center', gap: 18, opacity: prog(f, 2, 8)}}>
            <div style={{width: 80 * lineP, height: 3, background: AMBER, boxShadow: `0 0 12px ${AMBER}`}} />
            <div style={{fontFamily: SANS, fontWeight: 500, fontSize: 28, letterSpacing: '0.35em', color: '#8FB4DC'}}>{`FEATURE ${num} / ${String(total).padStart(2, '0')}`}</div>
          </div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 270, height: 420, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 50, paddingRight: isNew ? 110 : 0}}>
            <div style={{transform: `translateX(${(1 - sN) * -300}px) scale(${1 + (1 - sN) * 0.5})`, opacity: f >= 2 ? 1 : 0}}>
              <Glitch f={f} g={g}>{Num}</Glitch>
            </div>
            <div style={{width: 8, height: 320 * lineP, background: `linear-gradient(180deg, ${TEAL}, ${accent})`, boxShadow: `0 0 18px ${accent}`, borderRadius: 4}} />
            <div style={{display: 'flex', flexDirection: 'column', gap: 18}}>
              <div style={{position: 'relative'}}>
                <KChars text={title} f={f} t={4} size={tSize} stagger={1.1} color="#F4FAFF" glow={isNew ? 'rgba(242,163,58,0.5)' : 'rgba(76,168,255,0.55)'} />
                {isNew && (
                  <div style={{position: 'absolute', right: -150, top: -40, opacity: cl((f - 9) / 2), transform: `rotate(${-8 + (1 - sp(f, 9, 8, 320, 0.5)) * -30}deg) scale(${1 + (1 - sp(f, 9, 8, 320, 0.5)) * 2.4})`}}>
                    <div style={{fontFamily: SANS, fontWeight: 900, fontSize: 44, letterSpacing: '0.12em', color: '#1A0E00', padding: '4px 18px 4px 22px', borderRadius: 10,
                      background: `linear-gradient(135deg, #FFE08A, ${AMBER} 60%, #E8742A)`, boxShadow: `0 0 ${24 + 50 * kick(f, 9, 12)}px ${AMBER}`}}>NEW</div>
                  </div>
                )}
              </div>
              {sub && (
                <div style={{clipPath: `inset(-10px ${(1 - prog(f, 11, 20)) * 100}% -10px 0)`, transform: `translateX(${(1 - snap(f, 11)) * 60}px)`, opacity: f >= 11 ? 1 : 0}}>
                  <div style={{display: 'inline-block', fontFamily: SANS, fontWeight: 500, fontSize: 46, letterSpacing: '0.1em', color: isNew ? '#FFE3B0' : '#BFE2FF',
                    padding: '6px 22px', borderLeft: `5px solid ${accent}`, background: `linear-gradient(90deg, ${isNew ? 'rgba(242,163,58,0.18)' : 'rgba(76,168,255,0.16)'}, transparent)`}}>{sub}</div>
                </div>
              )}
            </div>
          </div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 820, display: 'flex', justifyContent: 'center', gap: 22}}>
            {Array.from({length: total}, (_, k) => k + 1).map((n) => {
              const on = n === idx, p = snap(f, 6 + n);
              return <div key={n} style={{width: on ? 80 : 24, height: 12, borderRadius: 6, transform: `scaleX(${Math.max(0, p)})`, background: on ? AMBER : n < idx ? TEAL : '#27456f',
                boxShadow: on ? `0 0 16px ${AMBER}` : undefined, opacity: n < idx ? 0.8 : 1}} />;
            })}
          </div>
        </AbsoluteFill>
        <Scan f={f} op={0.55} />
      </div>
      <Flash f={f} t={3} peak={0.25} dur={6} color="#DFF1FF" />
      <Wipe f={f} a={0} b={7} mode="reveal" />
      <Wipe f={f} a={31} b={39} mode="cover" />
    </Stage>
  );
};

// ============================================================ 4. ICON WALL
const IW = {count0: 15, count1: 60, move0: 66, move1: 77, cats: [77, 95, 123, 142], form: 199, usv: 213, links: 216, label: 222};
const CATS = [
  {cat: '无人', label: '无人', c: BLUE},
  {cat: '反无人', label: '反无人', c: AMBER},
  {cat: '指控信息', label: '指控信息', c: TEAL},
  {cat: '信息技术', label: '信息技术', c: '#8FB8FF'},
];
const PW = 420, PG = 30, PX0 = (1920 - (4 * PW + 3 * PG)) / 2, PY = 250, CELL = 80, GX = 10, GY = 82;
const byCat = (c: string) => ICONS.filter((i) => i.cat === c);
const PANEL_ICONS = CATS.map((c) => byCat(c.cat).slice(0, 30));
const OTHERS = ICONS.filter((i) => !CATS.some((c) => c.cat === i.cat));
const cellPos = (pi: number, j: number): [number, number] => [PX0 + pi * (PW + PG) + GX + (j % 5) * CELL + CELL / 2, PY + GY + Math.floor(j / 5) * CELL + CELL / 2];
const UCAV_J = PANEL_ICONS[0].findIndex((i) => i.key === 'uav_ucav');
const USV_J = PANEL_ICONS[0].findIndex((i) => i.key === 'usv_interceptor');
const V_POS: [number, number][] = [[960, 330], [770, 440], [1150, 440], [580, 550], [1340, 550]];
const USV_POS: [number, number][] = [[700, 760], [960, 760], [1220, 760]];
const BURST = Array.from({length: 40}).map((_, i) => ({key: ICONS[Math.floor(rnd(i * 3.1) * ICONS.length)].key, a: rnd(i * 1.7) * Math.PI * 2, d: 500 + rnd(i * 5.3) * 600, t: 15 + i * 1.15, s: 50 + rnd(i * 2.2) * 50}));

export const IconWallV5: React.FC = () => {
  const f = useCurrentFrame();
  const [sx, sy] = shakeXY(f, [...IW.cats, IW.form, IW.usv], 6);
  const cam = 1 + 0.05 * prog(f, 0, 279, lin) + 0.02 * IW.cats.reduce((a, t) => a + kick(f, t, 8), 0) + 0.03 * kick(f, IW.form, 12);
  const val = Math.round(331 * prog(f, IW.count0, IW.count1, (t) => 1 - Math.pow(1 - t, 3)));
  const mv = prog(f, IW.move0, IW.move1, inout);
  const cS = lerp(1, 0.42, mv), cX = lerp(960, 250, mv), cY = lerp(470, 132, mv);
  const dimP = prog(f, IW.form - 4, IW.form + 10);
  return (
    <Stage>
      <div style={{position: 'absolute', inset: 0, transform: `translate(${sx}px,${sy}px) scale(${cam})`, transformOrigin: '50% 50%'}}>
        <Backdrop glow={0.6} glowY={540} />
        {/* faint drifting wall of the other categories */}
        <div style={{position: 'absolute', inset: 0, opacity: 0.06 * prog(f, 0, 20)}}>
          {OTHERS.map((ic, i) => {
            const col = i % 18, row = Math.floor(i / 18);
            const y = ((row * 112 + 40 - f * 0.9) % 1120 + 1120) % 1120 - 60;
            return <Img key={ic.key} src={staticFile(`icons/${ic.key}.svg`)} style={{position: 'absolute', left: col * 108 + (row % 2) * 54 - 20, top: y, width: 72, height: 72}} />;
          })}
        </div>
        <Particles f={f} n={50} seed={11} op={0.7} />
        {/* burst of real icons while counting */}
        {BURST.map((b, i) => {
          const p = prog(f, b.t, b.t + 34, (t) => 1 - Math.pow(1 - t, 2));
          if (p <= 0 || p >= 1) return null;
          const x = 960 + Math.cos(b.a) * b.d * p, y = 470 + Math.sin(b.a) * b.d * 0.7 * p;
          return <Img key={i} src={staticFile(`icons/${b.key}.svg`)} style={{position: 'absolute', left: x - b.s / 2, top: y - b.s / 2, width: b.s, height: b.s, opacity: Math.sin(p * Math.PI) * 0.85, transform: `scale(${0.4 + p})`}} />;
        })}
        {/* panels */}
        <div style={{position: 'absolute', inset: 0, opacity: 1 - 0.86 * dimP, transform: `scale(${1 - 0.06 * dimP})`, transformOrigin: '50% 55%'}}>
          {CATS.map((c, pi) => {
            const T0 = IW.cats[pi];
            if (f < T0 - 1) return null;
            const s = sp(f, T0 - 1, 12, 210, 0.7);
            const fl = kick(f, T0 + 2, 14);
            const x = PX0 + pi * (PW + PG);
            const from = pi % 2 === 0 ? 1 : -1;
            return (
              <div key={pi} style={{position: 'absolute', left: x, top: PY, width: PW, height: 590, transform: `translateY(${(1 - s) * from * 420}px) rotate(${(1 - s) * from * 4}deg)`, opacity: cl(s * 2),
                borderRadius: 16, background: 'linear-gradient(180deg, rgba(18,38,74,0.88), rgba(9,22,46,0.88))', border: `2px solid ${c.c}${fl > 0.2 ? 'ff' : '77'}`,
                boxShadow: `0 0 ${20 + 60 * fl}px ${c.c}${fl > 0.2 ? 'aa' : '33'}`}}>
                <div style={{position: 'absolute', left: 20, right: 20, top: 14, height: 54, display: 'flex', alignItems: 'center', gap: 12, borderBottom: `1px solid ${c.c}55`}}>
                  <div style={{width: 8, height: 34, background: c.c, boxShadow: `0 0 12px ${c.c}`}} />
                  <KChars text={c.label} f={f} t={T0 + 1} size={42} stagger={1.5} color="#F2F8FF" glow={`${c.c}aa`} />
                  <div style={{marginLeft: 'auto', fontFamily: SANS, fontWeight: 700, fontSize: 24, color: c.c, opacity: prog(f, T0 + 6, T0 + 12)}}>{`${byCat(c.cat).length} 个`}</div>
                </div>
                {PANEL_ICONS[pi].map((ic, j) => {
                  const tj = T0 + 3 + ((j % 5) + Math.floor(j / 5)) * 1.1;
                  const si = sp(f, tj, 10, 280, 0.5);
                  if (si <= 0.001) return null;
                  const hide = pi === 0 && (j === UCAV_J || j === USV_J) && f >= IW.form - 2;
                  return (
                    <div key={ic.key} style={{position: 'absolute', left: GX + (j % 5) * CELL, top: GY + Math.floor(j / 5) * CELL, width: CELL, height: CELL, display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: 'radial-gradient(circle, rgba(190,220,255,0.09) 0%, transparent 68%)', opacity: hide ? 0.25 : 1}}>
                      <Img src={staticFile(`icons/${ic.key}.svg`)} style={{width: 66, height: 66, transform: `scale(${si})`}} />
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
        {/* counter */}
        {f >= IW.count0 - 1 && (
          <div style={{position: 'absolute', left: cX, top: cY, transform: `translate(-50%,-50%) scale(${cS})`, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: cl((f - IW.count0 + 2) / 3)}}>
            <div style={{display: 'flex', alignItems: 'baseline', fontFamily: BRAND, lineHeight: 1, transform: `scale(${1 + (1 - sp(f, IW.count0, 10, 260, 0.6)) * 0.8})`}}>
              <span style={{fontSize: 300, fontVariantNumeric: 'tabular-nums', ...gradTxt('#FFFFFF', '#58B0FF'), filter: 'drop-shadow(0 0 30px rgba(76,168,255,0.6))', width: 560, textAlign: 'center'}}>{val}</span>
            </div>
            <div style={{marginTop: 6}}><KChars text="三百多个拟物化图标" f={f} t={IW.count0 + 4} size={68} stagger={2.2} family={SANS} weight={700} ls="0.14em" /></div>
          </div>
        )}
        {/* formation */}
        {f >= IW.form - 2 && (
          <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
            {(() => {
              const p = prog(f, IW.links, IW.links + 12);
              const s = sp(f, IW.links, 12, 200, 0.7);
              return (
                <g opacity={p}>
                  {[1, 2, 3, 4].map((k) => {
                    const a = V_POS[k <= 2 ? 0 : k - 2], b = V_POS[k];
                    return <line key={k} x1={a[0]} y1={a[1]} x2={a[0] + (b[0] - a[0]) * p} y2={a[1] + (b[1] - a[1]) * p} stroke={TEAL} strokeWidth={2.5} strokeDasharray="10 7" />;
                  })}
                  <rect x={460 - 30 * (1 - s)} y={235 - 20 * (1 - s)} width={1000 + 60 * (1 - s)} height={410 + 40 * (1 - s)} rx={18} fill="none" stroke={BLUE} strokeWidth={2} strokeOpacity={0.7} strokeDasharray="16 10" />
                  {[[460, 235], [1460, 235], [460, 645], [1460, 645]].map(([x, y], i) => <rect key={i} x={x - 7} y={y - 7} width={14} height={14} fill={INK} stroke={BLUE} strokeWidth={2.5} />)}
                  <rect x={560} y={690} width={800} height={150} rx={18} fill="none" stroke={TEAL} strokeWidth={2} strokeOpacity={0.6 * prog(f, IW.usv + 8, IW.usv + 18)} strokeDasharray="16 10" />
                </g>
              );
            })()}
          </svg>
        )}
        {f >= IW.form - 2 && [...V_POS.map((p, k) => ({to: p, j: UCAV_J, key: 'uav_ucav', t: IW.form + k * 2.5, size: 150})),
          ...USV_POS.map((p, k) => ({to: p, j: USV_J, key: 'usv_interceptor', t: IW.usv + k * 2.5, size: 140}))].map((d, k) => {
          const [x0, y0] = cellPos(0, d.j);
          const s = sp(f, d.t, 13, 170, 0.8);
          if (s <= 0.001) return null;
          const x = lerp(x0, d.to[0], s), y = lerp(y0, d.to[1], s);
          const sc = lerp(66 / d.size, 1, Math.min(1, s));
          const lock = kick(f, d.t + 10, 12);
          return (
            <React.Fragment key={k}>
              <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
                {s < 0.95 && <line x1={x} y1={y} x2={lerp(x0, d.to[0], Math.max(0, s - 0.25))} y2={lerp(y0, d.to[1], Math.max(0, s - 0.25))} stroke={TEAL} strokeWidth={4} strokeLinecap="round" opacity={0.6} />}
                {lock > 0 && <circle cx={d.to[0]} cy={d.to[1]} r={d.size * (0.5 + (1 - lock) * 0.5)} fill="none" stroke={TEAL} strokeWidth={3} opacity={lock} />}
              </svg>
              <Img src={staticFile(`icons/${d.key}.svg`)} style={{position: 'absolute', left: x - d.size / 2, top: y - d.size / 2, width: d.size, height: d.size, transform: `scale(${sc})`,
                filter: `drop-shadow(0 0 ${10 + 20 * lock}px rgba(76,168,255,0.7))`}} />
            </React.Fragment>
          );
        })}
        {f >= IW.label && (
          <div style={{position: 'absolute', right: 90, top: 92, display: 'flex', alignItems: 'center', gap: 16}}>
            <KChars text="编队组合 · 随心搭配" f={f} t={IW.label} size={60} stagger={1.6} color="#F2F8FF" glow="rgba(43,212,196,0.6)" />
            <div style={{width: 10, height: 62, background: TEAL, boxShadow: `0 0 16px ${TEAL}`, transform: `scaleY(${sp(f, IW.label, 12, 260, 0.6)})`}} />
          </div>
        )}
        {IW.cats.map((t, i) => <Impact key={i} f={f} t={t} cx={PX0 + i * (PW + PG) + PW / 2} cy={PY + 300} n={10} r0={60} big={0.3} />)}
        <Impact f={f} t={IW.form + 12} cx={960} cy={440} n={14} r0={90} big={0.5} />
        <Scan f={f} op={0.5} />
      </div>
      {IW.cats.map((t) => <Flash key={t} f={f} t={t} peak={0.1} dur={4} />)}
      <Flash f={f} t={IW.form + 10} peak={0.15} dur={6} />
      <Wipe f={f} a={0} b={8} mode="reveal" />
    </Stage>
  );
};

// ============================================================ 5. OUTRO
const OT = {file: 20, inst: 42, off: 60, win: 83, kylin: 106, ft: 134, run: 167, out0: 195, out1: 207,
  kw: [214, 239, 259, 282, 303, 322], all: 346, conv0: 420, conv1: 433, title: 434, ver: 448, tag1: 466, tag2: 488, sweep: 500};
const KW4 = ['绿色', '离线', '免费', '高效', '好用', '普惠'];

const HtmlFile: React.FC<{f: number}> = ({f}) => (
  <svg width={240} height={290} viewBox="0 0 240 290" style={{overflow: 'visible'}}>
    <defs>
      <linearGradient id="hf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#1C3D73" /><stop offset="1" stopColor="#0B1E40" /></linearGradient>
    </defs>
    <path d="M20 10 H170 L220 60 V280 H20 Z" fill="url(#hf)" stroke={BLUE} strokeWidth={4} strokeLinejoin="round" />
    <path d="M170 10 V60 H220" fill="rgba(76,168,255,0.25)" stroke={BLUE} strokeWidth={4} strokeLinejoin="round" />
    <text x={120} y={150} textAnchor="middle" fontFamily="monospace" fontWeight={700} fontSize={42} fill="#E8F3FF">{'</>'}</text>
    {[0, 1, 2].map((i) => <rect key={i} x={52} y={185 + i * 24} width={(i === 1 ? 100 : 136) * prog(f, OT.file + 6 + i * 3, OT.file + 14 + i * 3)} height={8} rx={4} fill={i === 1 ? TEAL : BLUE} opacity={0.75} />)}
    <rect x={30} y={238} width={70} height={30} rx={6} fill={AMBER} />
    <text x={65} y={260} textAnchor="middle" fontFamily={SANS} fontWeight={900} fontSize={18} fill="#1A0E00">HTML</text>
  </svg>
);

const StatBig: React.FC<{f: number; t: number; big: string; label: string; color: string; x: number}> = ({f, t, big, label, color, x}) => {
  if (f < t) return null;
  const s = sp(f, t, 10, 260, 0.6);
  return (
    <div style={{position: 'absolute', left: x, top: 420, transform: `translate(-50%,-50%) scale(${1 + (1 - s) * 1.4})`, opacity: cl((f - t + 1) / 3), display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <div style={{fontFamily: BRAND, fontSize: 190, lineHeight: 1, ...gradTxt('#FFFFFF', color), filter: `drop-shadow(0 0 26px ${color}99)`, fontVariantNumeric: 'tabular-nums'}}>{big}</div>
      <div style={{marginTop: 8}}><KChars text={label} f={f} t={t + 3} size={60} stagger={2} family={SANS} weight={700} ls="0.3em" /></div>
    </div>
  );
};

export const OutroV5: React.FC = () => {
  const f = useCurrentFrame();
  const imp = [OT.file, OT.inst, OT.off, OT.win, OT.kylin, OT.ft, ...OT.kw, OT.title];
  const [sx, sy] = shakeXY(f, imp, 7);
  const cam = (f < OT.out0 ? 1 + 0.05 * prog(f, 0, OT.out0, lin) : f < OT.conv0 ? 1 + 0.04 * prog(f, OT.out1, OT.conv0, lin) : 1.08 - 0.08 * prog(f, OT.conv0, OT.title + 20) + 0.04 * prog(f, OT.title + 20, 585, lin))
    + 0.045 * kick(f, OT.title, 12) + 0.015 * imp.reduce((a, t) => a + kick(f, t, 6), 0) + 0.12 * prog(f, OT.out0, OT.out1, inout) * (f < OT.out1 ? 1 : 0);
  const out1 = prog(f, OT.out0, OT.out1, inout);
  const fileS = sp(f, OT.file, 9, 200, 0.7);
  const pct = Math.round(100 * prog(f, OT.off, OT.off + 16, (t) => 1 - Math.pow(1 - t, 3)));
  // chips
  const CW = 236, CG = 22, CH = 140, CY = 470;
  const totalW = 6 * CW + 5 * CG, x0 = 960 - totalW / 2 + CW / 2;
  const cc = prog(f, OT.conv0, OT.conv1, inout);
  const keepChips = 1 - prog(cc, 0.6, 1, lin);
  const ps = slam(f, OT.title);
  const g = kick(f, OT.title, 9);
  return (
    <Stage>
      <div style={{position: 'absolute', inset: 0, transform: `translate(${sx}px,${sy}px) scale(${cam})`, transformOrigin: '50% 48%'}}>
        <Backdrop glow={0.5 + 0.5 * prog(f, OT.title - 6, OT.title + 30)} glowY={lerp(500, 440, prog(f, OT.conv0, OT.title))} />
        {f >= OT.conv0 - 4 && (
          <div style={{position: 'absolute', inset: 0, opacity: 0.32, transform: 'scale(0.86)', transformOrigin: '50% 50%'}}>
            <Diagram start={OT.conv0 - 4} speed={2.4} pulseStart={OT.title + 10} />
          </div>
        )}
        <Particles f={f} n={55} seed={21} op={0.75} />

        {/* ---- beat 1: single file / offline / platforms ---- */}
        {f < OT.out1 && (
          <AbsoluteFill style={{opacity: 1 - out1, transform: `scale(${1 + out1 * 0.5})`, filter: out1 > 0 ? `blur(${out1 * 12}px)` : undefined}}>
            {f >= OT.file && (
              <div style={{position: 'absolute', left: 960 - 120, top: 400 - 145 - (1 - fileS) * 500, transform: `rotate(${(1 - fileS) * -18}deg) scale(${0.9 + 0.1 * fileS})`, opacity: cl((f - OT.file + 1) / 2),
                filter: `drop-shadow(0 0 ${20 + 40 * kick(f, OT.file + 6, 12)}px rgba(76,168,255,0.7))`}}>
                <HtmlFile f={f} />
              </div>
            )}
            {f >= OT.file + 4 && (
              <div style={{position: 'absolute', left: 0, right: 0, top: 590, display: 'flex', justifyContent: 'center'}}>
                <KChars text="单文件 · 经纬织图.html" f={f} t={OT.file + 4} size={40} stagger={0.8} family={SANS} weight={500} color="#CFE4FA" ls="0.08em" />
              </div>
            )}
            <StatBig f={f} t={OT.inst} big="0" label="安装" color="#58B0FF" x={430} />
            <StatBig f={f} t={OT.off} big={`${pct}%`} label="离线" color={TEAL} x={1490} />
            <div style={{position: 'absolute', left: 0, right: 0, top: 730, display: 'flex', justifyContent: 'center', gap: 34}}>
              {([[OT.win, 'Windows 7–11', BLUE], [OT.kylin, '银河麒麟 V10', TEAL], [OT.ft, '飞腾 D2000', AMBER]] as [number, string, string][]).map(([t, txt, c], i) => {
                if (f < t) return <div key={i} style={{width: 0}} />;
                const s = sp(f, t, 9, 300, 0.55);
                const ok = sp(f, OT.run + i * 4, 9, 320, 0.5);
                return (
                  <div key={i} style={{position: 'relative', transform: `translateY(${(1 - s) * 120}px) scale(${1 + (1 - s) * 0.6})`, opacity: cl((f - t + 1) / 3)}}>
                    <Badge text={txt} size={46} color={c} />
                    {f >= OT.run + i * 4 && (
                      <div style={{position: 'absolute', right: -20, top: -22, width: 46, height: 46, borderRadius: 23, background: TEAL, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        transform: `scale(${ok})`, boxShadow: `0 0 18px ${TEAL}`, fontFamily: SANS, fontWeight: 900, fontSize: 30, color: '#04201D'}}>✓</div>
                    )}
                  </div>
                );
              })}
            </div>
            {f >= OT.run && (
              <div style={{position: 'absolute', left: 0, right: 0, top: 830, display: 'flex', justifyContent: 'center'}}>
                <KChars text="实测可用" f={f} t={OT.run} size={44} stagger={2} family={SANS} weight={700} color="#8FF0E6" ls="0.3em" glow="rgba(43,212,196,0.6)" />
              </div>
            )}
          </AbsoluteFill>
        )}
        <Impact f={f} t={OT.file + 6} cx={960} cy={420} big={0.7} />
        <Impact f={f} t={OT.inst} cx={430} cy={400} n={10} r0={60} big={0.3} />
        <Impact f={f} t={OT.off} cx={1490} cy={400} n={10} r0={60} big={0.3} />

        {/* ---- beat 2: six value chips ---- */}
        {f >= OT.kw[0] && f < OT.conv1 + 2 && (
          <AbsoluteFill>
            {KW4.map((k, i) => {
              const t = OT.kw[i];
              if (f < t) return null;
              const s = sp(f, t, 10, 300, 0.6);
              const fl = kick(f, t, 14);
              const x = x0 + i * (CW + CG);
              const px = lerp(x, 960, cc), py = lerp(CY, 440, cc) - (1 - s) * 260;
              const accent = i % 2 === 0 ? BLUE : TEAL;
              return (
                <div key={i} style={{position: 'absolute', left: px - CW / 2, top: py - CH / 2, width: CW, height: CH, opacity: cl((f - t + 1) / 2) * keepChips,
                  transform: `rotate(${(1 - s) * (i % 2 ? 14 : -14)}deg) scale(${(1 + (1 - s) * 0.5) * (1 - 0.8 * cc)})`, borderRadius: 20,
                  background: `linear-gradient(180deg, rgba(${fl > 0.3 ? '44,100,176' : '16,38,76'},0.96), rgba(8,22,46,0.96))`, border: `3px solid ${i === 5 ? AMBER : accent}`,
                  boxShadow: `0 0 ${24 + fl * 70}px ${i === 5 ? AMBER : accent}${fl > 0.25 ? 'cc' : '55'}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: BRAND, fontSize: 74, letterSpacing: '0.12em', paddingLeft: '0.12em', color: '#F2F8FF', textShadow: `0 0 16px ${accent}99`}}>
                  {k}
                  <div style={{position: 'absolute', top: 10, left: 16, fontFamily: SANS, fontSize: 17, letterSpacing: 2, color: accent}}>{`0${i + 1}`}</div>
                </div>
              );
            })}
            {f >= OT.all && (
              <div style={{position: 'absolute', left: 0, right: 0, top: 640, display: 'flex', justifyContent: 'center', opacity: 1 - prog(f, OT.conv0 - 6, OT.conv0 + 4, lin)}}>
                <KChars text="人人都能画出专业的体系图" f={f} t={OT.all} size={64} stagger={2.6} family={SANS} weight={700} ls="0.1em" color={(i) => (i < 2 ? '#FFD27A' : '#EAF4FF')} />
              </div>
            )}
          </AbsoluteFill>
        )}
        {OT.kw.map((t, i) => <Impact key={i} f={f} t={t} cx={x0 + i * (CW + CG)} cy={CY} n={8} r0={50} big={0.25} />)}

        {/* ---- beat 3: lockup ---- */}
        {f >= OT.title && (
          <AbsoluteFill style={{alignItems: 'center'}}>
            <div style={{position: 'absolute', top: 420, transform: `translateY(-50%) scale(${1 + (1 - ps) * 1.0})`, opacity: cl((f - OT.title + 1) / 2)}}>
              <div style={{display: 'flex', alignItems: 'center', gap: 48}}>
                <Img src={staticFile('logo.svg')} style={{width: 172, height: 172, filter: 'drop-shadow(0 10px 30px rgba(10,40,90,0.8)) drop-shadow(0 0 24px rgba(76,168,255,0.45))'}} />
                <div style={{position: 'relative'}}>
                  <Glitch f={f} g={g}>{(tint) => <TitleTxt text="经纬织图" size={196} tint={tint} ls="0.08em" />}</Glitch>
                  <Sweep text="经纬织图" size={196} p={prog(f, OT.sweep, OT.sweep + 28, lin)} ls="0.08em" />
                  <div style={{position: 'absolute', right: -150, top: -18}}><VerBadge f={f} t={OT.ver} /></div>
                </div>
              </div>
            </div>
            <div style={{position: 'absolute', top: 636, left: 0, right: 0, display: 'flex', justifyContent: 'center', transform: 'translateY(-50%)'}}>
              {f >= OT.tag1 && <KChars text="把时间，" f={f} t={OT.tag1} size={66} stagger={2.4} family={SANS} weight={500} color="#DCEBFF" ls="0.12em" />}
              {f >= OT.tag2 && <KChars text="还给思考" f={f} t={OT.tag2} size={66} stagger={2.6} family={SANS} weight={700} color="#8FF0E6" ls="0.12em" glow="rgba(43,212,196,0.6)" />}
            </div>
            <div style={{position: 'absolute', top: 712, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
              <div style={{width: 940 * prog(f, OT.tag1, OT.tag1 + 18), height: 3, background: `linear-gradient(90deg, transparent, ${BLUE}, ${TEAL}, transparent)`, boxShadow: `0 0 14px ${BLUE}`}} />
            </div>
            <div style={{position: 'absolute', top: 764, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 26, opacity: prog(f, OT.tag2 + 20, OT.tag2 + 36), fontFamily: SANS, fontSize: 26, letterSpacing: '0.4em', color: '#8FB4DC'}}>
              {KW4.map((k, i) => <span key={i}>{k}</span>)}
            </div>
          </AbsoluteFill>
        )}
        <Impact f={f} t={OT.title} cx={960} cy={420} big={1.1} />
        <Streaks f={f} a={OT.title - 2} b={OT.title + 12} />
        <Streaks f={f} a={OT.out0} b={OT.out1 + 4} dir={-1} />
        <Scan f={f} op={0.5} />
      </div>
      <Flash f={f} t={OT.title} peak={0.8} dur={9} color="#DFF1FF" />
      <Flash f={f} t={OT.out1 - 4} peak={0.2} dur={6} />
      {OT.kw.map((t) => <Flash key={t} f={f} t={t} peak={0.08} dur={4} />)}
      <Wipe f={f} a={0} b={9} mode="reveal" />
    </Stage>
  );
};
