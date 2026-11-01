import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Easing, interpolate, spring, staticFile, delayRender, continueRender, cancelRender, useCurrentFrame} from 'remotion';
import {getLength, getPointAtLength} from '@remotion/paths';

export const BLUE = '#4CA8FF';
export const TEAL = '#2BD4C4';
export const AMBER = '#F2A33A';
export const INK = '#050B18';
export const BRAND = "'Smiley Sans', 'Noto Sans CJK SC', sans-serif";
export const SANS = "'Noto Sans CJK SC', sans-serif";

export const ease = Easing.bezier(0.22, 1, 0.36, 1);
export const inout = Easing.bezier(0.65, 0, 0.35, 1);
export const prog = (f: number, a: number, b: number, e: (t: number) => number = ease) =>
  interpolate(f, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const FPS = 30;
export const pop = (f: number, delay: number) =>
  spring({frame: f - delay, fps: FPS, config: {damping: 15, stiffness: 150, mass: 0.8}});

// ---------- stage (fonts + root) ----------
export const Stage: React.FC<{children: React.ReactNode}> = ({children}) => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    const f = new FontFace('Smiley Sans', `url(${staticFile('fonts/SmileySans-Oblique.ttf')})`);
    Promise.all([
      f.load(),
      document.fonts.load('500 40px "Noto Sans CJK SC"', '经纬织图鸿图体系绘图使用教程'),
      document.fonts.load('300 40px "Noto Sans CJK SC"', '让画图快起来'),
      document.fonts.load('400 40px "Noto Sans CJK SC"', '绿色离线免费'),
    ])
      .then(([ff]) => {
        document.fonts.add(ff as FontFace);
        return document.fonts.load('60px "Smiley Sans"', '经纬织图体系绘图感谢观看绿色离线免费高效好用普惠互通与转换模板导出');
      })
      .then(() => continueRender(handle))
      .catch((e) => cancelRender(e));
  }, [handle]);
  return (
    <AbsoluteFill lang="zh-CN" style={{background: INK, fontFamily: SANS, overflow: 'hidden'}}>
      {children}
    </AbsoluteFill>
  );
};

// ---------- backdrop ----------
const UAV_FW = 'M0,-60 L8,-20 L70,10 L70,22 L8,12 L6,45 L24,56 L24,64 L0,58 L-24,64 L-24,56 L-6,45 L-8,12 L-70,22 L-70,10 L-8,-20 Z';
const SHIP = 'M-90,0 L90,0 L70,22 L-70,22 Z M-20,0 L-14,-16 L30,-16 L36,0 M10,-16 L10,-36 M-4,-16 L-4,-26 L8,-26';

const Quad: React.FC<{f: number}> = ({f}) => (
  <g>
    <rect x={-12} y={-12} width={24} height={24} rx={5} />
    {[45, 135, 225, 315].map((a) => {
      const r = (a * Math.PI) / 180;
      const x = Math.cos(r) * 52, y = Math.sin(r) * 52;
      return (
        <g key={a}>
          <line x1={Math.cos(r) * 12} y1={Math.sin(r) * 12} x2={x} y2={y} />
          <circle cx={x} cy={y} r={22} strokeDasharray="5 6" />
          <g transform={`translate(${x},${y}) rotate(${f * 14 * (a % 90 === 45 && a < 200 ? 1 : -1)})`}>
            <line x1={-18} y1={0} x2={18} y2={0} />
          </g>
        </g>
      );
    })}
  </g>
);

const SIL = [
  {t: 'quad', y: 600, x0: 200, v: 0.55, s: 1.9, o: 0.11, rot: 0},
  {t: 'fw', y: 470, x0: 1500, v: -0.8, s: 1.5, o: 0.1, rot: 90},
  {t: 'ship', y: 700, x0: 1300, v: -0.35, s: 2.1, o: 0.09, rot: 0},
  {t: 'fw', y: 420, x0: 300, v: 0.45, s: 1.0, o: 0.07, rot: -90},
];

export const Silhouettes: React.FC<{f: number; fade?: number}> = ({f, fade = 1}) => (
  <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, opacity: fade}}>
    {SIL.map((s, i) => {
      const x = ((s.x0 + s.v * f + 400) % 2640 + 2640) % 2640 - 400;
      return (
        <g key={i} transform={`translate(${x},${s.y + Math.sin(f / 40 + i) * 8}) rotate(${s.rot}) scale(${s.s})`}
           fill="none" stroke="#8CC4FF" strokeOpacity={s.o * 1.8} strokeWidth={1.4 / s.s} strokeLinejoin="round">
          {s.t === 'quad' && <Quad f={f} />}
          {s.t === 'fw' && <path d={UAV_FW} />}
          {s.t === 'ship' && <path d={SHIP} />}
        </g>
      );
    })}
  </svg>
);

export const Backdrop: React.FC<{glow?: number; glowY?: number}> = ({glow = 0.0, glowY = 540}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 80% 75% at 50% 48%, #0F2142 0%, #09162E 45%, #050B18 100%)'}} />
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <defs>
          <pattern id="g1" width={40} height={40} patternUnits="userSpaceOnUse" x={-(f * 0.12) % 40} y={0}>
            <path d="M40 0H0V40" fill="none" stroke={BLUE} strokeOpacity={0.07} strokeWidth={1} />
          </pattern>
          <pattern id="g2" width={200} height={200} patternUnits="userSpaceOnUse" x={-(f * 0.12) % 200} y={0}>
            <path d="M200 0H0V200" fill="none" stroke={BLUE} strokeOpacity={0.13} strokeWidth={1} />
          </pattern>
        </defs>
        <rect width={1920} height={1080} fill="url(#g1)" />
        <rect width={1920} height={1080} fill="url(#g2)" />
        {/* corner registration brackets */}
        {[[24, 24, 1, 1], [1896, 24, -1, 1], [24, 1056, 1, -1], [1896, 1056, -1, -1]].map(([x, y, sx, sy], i) => (
          <path key={i} d={`M${x} ${y + 36 * sy}V${y}H${x + 36 * sx}`} fill="none" stroke={BLUE} strokeOpacity={0.45} strokeWidth={1.5} />
        ))}
      </svg>
      <Silhouettes f={f} />
      {glow > 0 && (
        <AbsoluteFill style={{background: `radial-gradient(ellipse 36% 30% at 50% ${(glowY / 1080) * 100}%, rgba(76,168,255,${0.2 * glow}) 0%, rgba(43,212,196,${0.05 * glow}) 55%, transparent 100%)`}} />
      )}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 75% 75% at 50% 50%, transparent 55%, rgba(2,5,12,0.75) 100%)'}} />
    </AbsoluteFill>
  );
};

// ---------- diagram ----------
const XS = [250, 620, 960, 1300, 1670];
const TOP_Y = 185, BOT_Y = 895, NW = 230, NH = 84;
const topL = ['感知节点', '数据链路', '指挥控制', '任务规划', '态势显示'];
const botL = ['无人机', '无人艇', '地面站', '任务载荷', '综合保障'];
const topC = [BLUE, TEAL, BLUE, TEAL, BLUE];
const botC = [TEAL, BLUE, TEAL, BLUE, TEAL];
export const NODES = [
  ...XS.map((x, i) => ({id: i, x, y: TOP_Y, label: topL[i], c: topC[i], amber: i === 2})),
  ...XS.map((x, i) => ({id: 5 + i, x, y: BOT_Y, label: botL[i], c: botC[i], amber: false})),
];
const BANDS = [
  {y: 80, h: 210, label: '感知层'},
  {y: 790, h: 210, label: '执行层'},
];
const BUS1 = 'M120 340 L240 340 A10 10 0 0 1 260 340 L1660 340 A10 10 0 0 1 1680 340 L1800 340';
const BUS2 = 'M120 740 L240 740 A10 10 0 0 1 260 740 L1660 740 A10 10 0 0 1 1680 740 L1800 740';
type Link = {d: string; c: string; ang?: number; end?: [number, number]; dot?: boolean; w?: number};
const LINKS: Link[] = [
  ...[0, 1, 2, 3].map((i): Link => ({d: `M${XS[i] + 115} ${TOP_Y} L${XS[i + 1] - 115 - 2} ${TOP_Y}`, c: BLUE, ang: 0, end: [XS[i + 1] - 115, TOP_Y]})),
  ...[0, 1, 2, 3].map((i): Link => ({d: `M${XS[i + 1] - 115} ${BOT_Y} L${XS[i] + 115 + 2} ${BOT_Y}`, c: TEAL, ang: 180, end: [XS[i] + 115, BOT_Y]})),
  {d: 'M250 227 L250 851', c: BLUE, ang: 90, end: [250, 853]},
  {d: 'M1670 853 L1670 229', c: TEAL, ang: -90, end: [1670, 227]},
  {d: 'M620 227 L620 340', c: BLUE},
  {d: 'M1300 227 L1300 340', c: BLUE},
  {d: 'M620 740 L620 851', c: TEAL, ang: 90, end: [620, 853]},
  {d: 'M1300 740 L1300 851', c: TEAL, ang: 90, end: [1300, 853]},
  {d: BUS1, c: TEAL, w: 1.8},
  {d: BUS2, c: BLUE, w: 1.8},
];
const JUNCTIONS: [number, number, string][] = [[620, 340, TEAL], [1300, 340, TEAL], [620, 740, BLUE], [1300, 740, BLUE]];
const CAPS: [number, number, string][] = [[120, 340, TEAL], [1800, 340, TEAL], [120, 740, BLUE], [1800, 740, BLUE]];
const LEN = LINKS.map((l) => getLength(l.d));
const PULSES = [
  {li: 8, per: 70, ph: 0.1, c: '#9FD3FF'}, {li: 9, per: 70, ph: 0.55, c: '#7FF0E4'},
  {li: 0, per: 60, ph: 0.0, c: '#9FD3FF'}, {li: 1, per: 60, ph: 0.3, c: '#9FD3FF'}, {li: 2, per: 60, ph: 0.6, c: AMBER}, {li: 3, per: 60, ph: 0.8, c: '#9FD3FF'},
  {li: 4, per: 64, ph: 0.2, c: '#7FF0E4'}, {li: 5, per: 64, ph: 0.5, c: '#7FF0E4'}, {li: 7, per: 64, ph: 0.9, c: '#7FF0E4'},
  {li: 12, per: 52, ph: 0.4, c: '#7FF0E4'}, {li: 13, per: 52, ph: 0.7, c: '#9FD3FF'},
  {li: 14, per: 150, ph: 0.0, c: '#7FF0E4'}, {li: 15, per: 170, ph: 0.35, c: '#9FD3FF'},
  {li: 14, per: 150, ph: 0.5, c: '#7FF0E4'}, {li: 15, per: 170, ph: 0.85, c: '#9FD3FF'},
];

export type DiagramProps = {
  start: number; speed?: number; pulseStart: number;
  conv?: {c0: number; c1: number; cx: number; cy: number};
};

export const Diagram: React.FC<DiagramProps> = ({start, speed = 1, pulseStart, conv}) => {
  const frame = useCurrentFrame();
  const b = (frame - start) * speed;
  const cc = conv ? prog(frame, conv.c0, conv.c1, inout) : 0;
  const ccAt = (i: number) => (conv ? prog(frame, conv.c0 + i * 1.2, conv.c1 + i * 1.2, inout) : 0);
  const bandKeep = 1 - 0.55 * cc;
  const linkKeep = 1 - prog(cc, 0, 0.45, Easing.linear);

  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      <defs>
        <filter id="glow" x="-30%" y="-60%" width="160%" height="220%">
          <feGaussianBlur stdDeviation="5" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <filter id="glowS" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="3.5" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      {/* bands */}
      <g opacity={bandKeep}>
        {/* mid zone, very faint */}
        <rect x={30} y={340} width={1860} height={400} fill={BLUE} fillOpacity={0.018 * prog(b, 8, 40)} />
        {BANDS.map((bd, i) => {
          const p = prog(b, 2 + i * 6, 34 + i * 6);
          return (
            <g key={i}>
              <rect x={30} y={bd.y} width={1860} height={bd.h} rx={14} fill={BLUE} fillOpacity={0.045 * p}
                    stroke={BLUE} strokeOpacity={0.4} strokeWidth={1.4} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
              <text x={50} y={bd.y + 34} fontSize={19} fill={BLUE} fillOpacity={0.75 * prog(b, 22, 40)} letterSpacing={5} fontFamily={SANS} fontWeight={500}>{bd.label}</text>
              <path d={`M50 ${bd.y + 46}H${50 + 80 * prog(b, 24, 44)}`} stroke={BLUE} strokeOpacity={0.5} strokeWidth={1.4} />
            </g>
          );
        })}
      </g>

      {/* links */}
      {LINKS.map((l, i) => {
        const t0 = 26 + i * 3.2;
        const p = prog(b, t0, t0 + 24, Easing.bezier(0.3, 0.6, 0.3, 1));
        const op = linkKeep;
        const a = l.ang !== undefined && l.end ? pop(b, t0 + 22) : 0;
        return (
          <g key={i} opacity={op}>
            <path d={l.d} fill="none" stroke={l.c} strokeOpacity={0.22} strokeWidth={(l.w ?? 2.2) + 6} pathLength={1}
                  strokeDasharray={1} strokeDashoffset={1 - p} strokeLinecap="butt" strokeLinejoin="round" />
            <path d={l.d} fill="none" stroke={l.c} strokeOpacity={0.95} strokeWidth={l.w ?? 2.2} pathLength={1}
                  strokeDasharray={1} strokeDashoffset={1 - p} strokeLinecap="butt" strokeLinejoin="round" />
            {l.ang !== undefined && l.end && a > 0.01 && (
              <g transform={`translate(${l.end[0]},${l.end[1]}) rotate(${l.ang}) scale(${a})`}>
                <path d="M0 0 L-15 -8 L-11 0 L-15 8 Z" fill={l.c} />
              </g>
            )}
          </g>
        );
      })}
      <g opacity={linkKeep}>
        {JUNCTIONS.map(([x, y, c], i) => (
          <circle key={i} cx={x} cy={y} r={6 * pop(b, 52 + i * 3)} fill={INK} stroke={c} strokeWidth={2.2} filter="url(#glowS)" />
        ))}
        {CAPS.map(([x, y, c], i) => {
          const s = pop(b, 30 + i * 2);
          return <rect key={i} x={x - 6 * s} y={y - 6 * s} width={12 * s} height={12 * s} fill={INK} stroke={c} strokeWidth={2} />;
        })}
      </g>

      {/* pulses */}
      <g opacity={linkKeep}>
        {PULSES.map((pl, k) => {
          const age = frame - pulseStart;
          if (age < 0) return null;
          const u = (((age + pl.ph * pl.per) / pl.per) % 1 + 1) % 1;
          const fadeIn = prog(age, 0, 12, Easing.linear);
          const len = LEN[pl.li];
          const parts = [0, 1, 2, 3, 4].map((j) => {
            const uu = u - j * (22 / len);
            if (uu < 0) return null;
            const pt = getPointAtLength(LINKS[pl.li].d, uu * len);
            const env = Math.min(1, uu * len / 20, (1 - uu) * len / 20);
            return <circle key={j} cx={pt.x} cy={pt.y} r={j === 0 ? 5.5 : 4.5 - j * 0.7} fill={j === 0 ? '#fff' : pl.c}
                           opacity={(j === 0 ? 1 : 0.55 - j * 0.1) * env * fadeIn} />;
          });
          return <g key={k} filter="url(#glowS)" style={{color: pl.c}}>{parts}</g>;
        })}
      </g>

      {/* speed streaks during convergence */}
      {conv && NODES.map((n, i) => {
        const c = ccAt(i);
        if (c <= 0.02 || c >= 0.98) return null;
        const x = lerp(n.x, conv.cx, c), y = lerp(n.y, conv.cy, c);
        const tx = lerp(n.x, conv.cx, Math.max(0, c - 0.22)), ty = lerp(n.y, conv.cy, Math.max(0, c - 0.22));
        return <line key={i} x1={x} y1={y} x2={tx} y2={ty} stroke={n.c} strokeWidth={3} strokeLinecap="round" opacity={Math.sin(c * Math.PI) * 0.65} />;
      })}

      {/* nodes */}
      <g filter="url(#glow)">
        {NODES.map((n, i) => {
          const s = pop(b, 14 + i * 2.6);
          const c = ccAt(i);
          const x = lerp(n.x, conv ? conv.cx : n.x, c), y = lerp(n.y, conv ? conv.cy : n.y, c);
          const sc = Math.max(0, s) * (1 - 0.82 * c);
          const op = Math.min(1, Math.max(0, s) * 1.4) * (1 - prog(c, 0.55, 1, Easing.linear));
          if (op <= 0.01) return null;
          return (
            <g key={i} transform={`translate(${x},${y}) scale(${sc})`} opacity={op}>
              <rect x={-NW / 2} y={-NH / 2} width={NW} height={NH} rx={10} fill="#0A1A36" fillOpacity={0.92} stroke={n.c} strokeWidth={1.8} />
              <rect x={-NW / 2} y={-NH / 2 + 14} width={4} height={NH - 28} fill={n.c} />
              <path d={`M${NW / 2 - 26} ${-NH / 2}H${NW / 2}V${-NH / 2 + 26}`} fill="none" stroke={n.c} strokeOpacity={0.6} strokeWidth={1.4} />
              <text x={-6} y={9} textAnchor="middle" fontSize={27} fontWeight={500} fill="#E6F1FF" fontFamily={SANS} letterSpacing={2}>{n.label}</text>
              <circle cx={NW / 2 - 18} cy={NH / 2 - 17} r={4} fill={n.amber ? AMBER : n.c} />
            </g>
          );
        })}
      </g>
    </svg>
  );
};

// ---------- text ----------
export const Chars: React.FC<{
  text: string; frame: number; start: number; stagger?: number; size: number; family?: string; color?: string;
  ls?: string; weight?: number; sweep?: number | null; glow?: string; dur?: number; rise?: number;
}> = ({text, frame, start, stagger = 3.5, size, family = BRAND, color = '#EEF6FF', ls = '0.06em', weight = 400, sweep = null, glow = 'rgba(76,168,255,0.6)', dur = 22, rise = 44}) => {
  const chars = Array.from(text);
  const common: React.CSSProperties = {fontFamily: family, fontSize: size, fontWeight: weight, letterSpacing: ls, whiteSpace: 'pre', lineHeight: 1.1};
  return (
    <div style={{position: 'relative', display: 'inline-block'}}>
      <div style={{...common, display: 'flex', color}}>
        {chars.map((ch, i) => {
          const p = prog(frame, start + i * stagger, start + i * stagger + dur);
          return (
            <span key={i} style={{display: 'inline-block', opacity: Math.min(1, p * 1.6), transform: `translateY(${(1 - p) * rise}px) scale(${1 + (1 - p) * 0.12})`,
              filter: p < 1 ? `blur(${(1 - p) * 14}px)` : undefined,
              textShadow: `0 0 ${24 * prog(p, 0.4, 1)}px ${glow}, 0 0 3px rgba(255,255,255,0.35)`}}>{ch}</span>
          );
        })}
      </div>
      {sweep !== null && sweep > 0 && sweep < 1 && (
        <div style={{...common, position: 'absolute', left: 0, top: 0, color: 'transparent', WebkitBackgroundClip: 'text', backgroundClip: 'text',
          backgroundImage: 'linear-gradient(100deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0) 41%, rgba(190,235,255,0.95) 50%, rgba(255,255,255,0) 59%, rgba(255,255,255,0) 100%)',
          backgroundSize: '300% 100%', backgroundRepeat: 'no-repeat', backgroundPosition: `${100 - sweep * 100}% 0`}}>{text}</div>
      )}
    </div>
  );
};

export const Rule: React.FC<{p: number; w: number; color?: string; diamond?: boolean}> = ({p, w, color = BLUE, diamond}) => (
  <div style={{position: 'relative', width: w, height: 10, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
    <div style={{width: w * p, height: 2, background: `linear-gradient(90deg, transparent, ${color} 30%, ${color} 70%, transparent)`, opacity: 0.9}} />
    {diamond && <div style={{position: 'absolute', width: 10, height: 10, transform: `rotate(45deg) scale(${p})`, background: AMBER, boxShadow: `0 0 12px ${AMBER}`}} />}
  </div>
);
