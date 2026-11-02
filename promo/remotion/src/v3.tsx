import React from 'react';
import {spring} from 'remotion';
import {AMBER, BLUE, BRAND, INK, TEAL, inout, prog} from './common';

export const rnd = (n: number) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
export const kick = (f: number, t: number, dur = 10) => (f < t || f >= t + dur ? 0 : Math.pow(1 - (f - t) / dur, 2));
export const shakeXY = (f: number, imp: number[], amp: number): [number, number] => {
  let dx = 0, dy = 0;
  for (const t of imp) { const k = kick(f, t, 9); dx += (rnd(f * 1.3 + t) - 0.5) * 2 * amp * k; dy += (rnd(f * 2.1 + t * 3) - 0.5) * 2 * amp * k; }
  return [dx, dy];
};
export const slam = (f: number, t: number) => spring({frame: f - t, fps: 30, config: {damping: 11, stiffness: 260, mass: 0.6}});
export const snap = (f: number, t: number) => spring({frame: f - t, fps: 30, config: {damping: 13, stiffness: 320, mass: 0.7}});

export const Flash: React.FC<{f: number; t: number; peak?: number; dur?: number; color?: string}> = ({f, t, peak = 0.7, dur = 7, color = '#fff'}) => {
  const k = kick(f, t, dur);
  return k > 0 ? <div style={{position: 'absolute', inset: 0, background: color, opacity: peak * k, pointerEvents: 'none'}} /> : null;
};

export const Impact: React.FC<{f: number; t: number; cx: number; cy: number; n?: number; r0?: number; big?: number}> = ({f, t, cx, cy, n = 26, r0 = 120, big = 1}) => {
  const p = prog(f, t, t + 16, (x) => 1 - Math.pow(1 - x, 3));
  if (p <= 0 || p >= 1) return null;
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      <circle cx={cx} cy={cy} r={40 + p * 760 * big} fill="none" stroke={BLUE} strokeWidth={7 * (1 - p)} opacity={1 - p} />
      <circle cx={cx} cy={cy} r={20 + p * 480 * big} fill="none" stroke={TEAL} strokeWidth={4 * (1 - p)} opacity={(1 - p) * 0.9} />
      {Array.from({length: n}).map((_, i) => {
        const a = (i / n) * Math.PI * 2 + rnd(i) * 0.2;
        const r1 = r0 + p * (380 + rnd(i + 9) * 380) * big, r2 = r1 + 90 * (1 - p) * (0.5 + rnd(i + 3));
        return <line key={i} x1={cx + Math.cos(a) * r1} y1={cy + Math.sin(a) * r1} x2={cx + Math.cos(a) * r2} y2={cy + Math.sin(a) * r2}
          stroke={i % 3 === 0 ? AMBER : i % 2 ? '#BDE3FF' : TEAL} strokeWidth={3.5} strokeLinecap="round" opacity={1 - p} />;
      })}
    </svg>
  );
};

// RGB split + slice glitch around a render-prop child
export const Glitch: React.FC<{f: number; g: number; children: (tint?: string) => React.ReactNode}> = ({f, g, children}) => {
  if (g <= 0.02) return <>{children()}</>;
  const d = g * 22 * (rnd(f * 3.7) > 0.5 ? 1 : -1);
  const slices = [0, 1, 2].map((i) => {
    const top = rnd(f * 5 + i * 11) * 80, h = 8 + rnd(f * 7 + i) * 22;
    return {top, h, dx: (rnd(f * 9 + i * 5) - 0.5) * 120 * g};
  });
  return (
    <div style={{position: 'relative'}}>
      <div style={{position: 'absolute', left: 0, top: 0, transform: `translateX(${-d}px)`, mixBlendMode: 'screen', opacity: 0.85}}>{children('#18E3D2')}</div>
      <div style={{position: 'absolute', left: 0, top: 0, transform: `translateX(${d}px)`, mixBlendMode: 'screen', opacity: 0.85}}>{children('#FF3D71')}</div>
      <div style={{position: 'relative', transform: `translateX(${slices[0].dx * 0.2}px)`}}>{children()}</div>
      {slices.map((s, i) => (
        <div key={i} style={{position: 'absolute', left: 0, top: 0, transform: `translateX(${s.dx}px)`, clipPath: `inset(${s.top}% 0 ${Math.max(0, 100 - s.top - s.h)}% 0)`}}>{children()}</div>
      ))}
    </div>
  );
};

export const TitleTxt: React.FC<{text: string; size: number; tint?: string; ls?: string}> = ({text, size, tint, ls = '0.05em'}) => (
  <div style={{fontFamily: BRAND, fontSize: size, letterSpacing: ls, paddingLeft: ls, lineHeight: 1.12, whiteSpace: 'pre',
    ...(tint ? {color: tint} : {color: 'transparent', backgroundImage: 'linear-gradient(180deg,#FFFFFF 6%,#D2ECFF 42%,#58B0FF 100%)',
      WebkitBackgroundClip: 'text', backgroundClip: 'text', filter: 'drop-shadow(0 0 26px rgba(76,168,255,0.55))'})}}>{text}</div>
);

export const Sweep: React.FC<{text: string; size: number; p: number; ls?: string}> = ({text, size, p, ls = '0.05em'}) =>
  p > 0 && p < 1 ? (
    <div style={{position: 'absolute', left: 0, top: 0, fontFamily: BRAND, fontSize: size, letterSpacing: ls, paddingLeft: ls, lineHeight: 1.12, whiteSpace: 'pre', color: 'transparent',
      WebkitBackgroundClip: 'text', backgroundClip: 'text', backgroundRepeat: 'no-repeat', backgroundSize: '300% 100%', backgroundPosition: `${100 - p * 100}% 0`,
      backgroundImage: 'linear-gradient(100deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0) 41%, rgba(210,242,255,1) 50%, rgba(255,255,255,0) 59%, rgba(255,255,255,0) 100%)'}}>{text}</div>
  ) : null;

// scan wipe: bar travels left->right. mode 'cover' = INK fills left of bar; 'reveal' = INK remains right of bar.
export const Wipe: React.FC<{f: number; a: number; b: number; mode: 'cover' | 'reveal'}> = ({f, a, b, mode}) => {
  const p = prog(f, a, b, inout);
  if (mode === 'cover' && p <= 0) return null;
  if (mode === 'reveal' && p >= 1) return null;
  const x = -160 + p * 2240, sk = 90;
  const poly = mode === 'cover'
    ? `0,0 ${x + sk},0 ${x - sk},1080 0,1080`
    : `${x + sk},0 1920,0 1920,1080 ${x - sk},1080`;
  const trail = `${x + sk - 260},0 ${x + sk},0 ${x - sk},1080 ${x - sk - 260},1080`;
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      <defs>
        <linearGradient id="trl" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stopColor={BLUE} stopOpacity="0" /><stop offset="1" stopColor={BLUE} stopOpacity="0.55" /></linearGradient>
      </defs>
      <polygon points={poly} fill={INK} />
      <polygon points={trail} fill="url(#trl)" opacity={mode === 'cover' ? 0 : 0} />
      <line x1={x + sk} y1={0} x2={x - sk} y2={1080} stroke="#fff" strokeWidth={5} style={{filter: `drop-shadow(0 0 14px ${BLUE}) drop-shadow(0 0 30px ${TEAL})`}} />
      <line x1={x + sk - 34} y1={0} x2={x - sk - 34} y2={1080} stroke={TEAL} strokeWidth={2} opacity={0.8} />
      <line x1={x + sk - 70} y1={0} x2={x - sk - 70} y2={1080} stroke={BLUE} strokeWidth={2} opacity={0.5} />
    </svg>
  );
};

export const ScanLine: React.FC<{p: number}> = ({p}) =>
  p > 0 && p < 1 ? (
    <div style={{position: 'absolute', left: 0, right: 0, top: p * 1080 - 60, height: 120,
      background: 'linear-gradient(180deg, rgba(76,168,255,0) 0%, rgba(120,200,255,0.35) 92%, rgba(220,245,255,0.95) 100%)', pointerEvents: 'none'}} />
  ) : null;
