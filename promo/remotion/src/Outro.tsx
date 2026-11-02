import React from 'react';
import {AbsoluteFill, Easing, useCurrentFrame} from 'remotion';
import {AMBER, BLUE, BRAND, Backdrop, Chars, Diagram, Rule, SANS, Stage, TEAL, INK, inout, lerp, pop, prog} from './common';

const KW = ['绿色', '离线', '免费', '高效', '好用', '普惠'];
const KT = [40, 52, 64, 76, 88, 100];
const CW = 200, CG = 22, CH = 100, CY = 540;
const C0 = 124, C1 = 158;

export const Outro: React.FC<{org?: string}> = ({org = '经纬织图开发组'}) => {
  const f = useCurrentFrame();
  const cx = 960, cy = 470;
  const cc = prog(f, C0, C1, inout);
  const totalW = 6 * CW + 5 * CG;
  const x0 = 960 - totalW / 2 + CW / 2;
  const sweep1 = prog(f, 184, 212, (t) => t);
  const sweep2 = prog(f, 252, 280, (t) => t);
  const shift = prog(f, 212, 238, inout);
  const sloP = prog(f, 176, 200);
  const orgP = prog(f, 196, 216);
  const glow = prog(f, 150, 190) * (1 - 0.35 * shift);
  const ring = (d: number) => prog(f, C1 + d, C1 + d + 34);
  const axisP = prog(f, 36, 106, Easing.linear);
  const fadeIn = prog(f, 0, 8, (t) => t);
  const keepChips = 1 - prog(cc, 0.55, 1, (t) => t);

  return (
    <Stage>
      <Backdrop glow={glow} glowY={lerp(470, 400, shift)} />
      <Diagram start={4} speed={1.4} pulseStart={40} conv={{c0: C0, c1: C1, cx, cy}} />

      {/* chips */}
      {f < C1 && (
        <AbsoluteFill>
          <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
            <line x1={x0 - CW / 2 - 40} y1={CY} x2={x0 - CW / 2 - 40 + (totalW + 80) * axisP} y2={CY} stroke={BLUE} strokeOpacity={0.35 * keepChips} strokeWidth={1.5} strokeDasharray="2 8" />
          </svg>
          {KW.map((k, i) => {
            const s = Math.max(0, pop(f, KT[i]));
            const flash = 1 - prog(f, KT[i], KT[i] + 20);
            const x = x0 + i * (CW + CG);
            const c = lerp(0, 1, cc);
            const px = lerp(x, cx, c), py = lerp(CY, cy, c);
            const accent = i % 2 === 0 ? BLUE : TEAL;
            const op = Math.min(1, s * 1.5) * keepChips;
            return (
              <div key={i} style={{position: 'absolute', left: px - CW / 2, top: py - CH / 2, width: CW, height: CH, opacity: op,
                transform: `scale(${(0.7 + 0.3 * s) * (1 - 0.8 * c)})`, borderRadius: 16,
                background: 'linear-gradient(180deg, rgba(16,38,76,0.95), rgba(8,22,46,0.95))', border: `2px solid ${accent}`,
                boxShadow: `0 0 ${22 + flash * 40}px ${accent}${flash > 0.3 ? 'aa' : '55'}, inset 0 0 22px ${accent}22`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: BRAND, fontSize: 52, letterSpacing: '0.12em', paddingLeft: '0.12em', color: '#F2F8FF',
                textShadow: `0 0 16px ${accent}99`}}>
                {k}
                <div style={{position: 'absolute', top: 10, left: 14, fontFamily: SANS, fontSize: 14, letterSpacing: 2, color: accent, opacity: 0.85}}>{`0${i + 1}`}</div>
                <div style={{position: 'absolute', right: 14, bottom: 12, width: 8, height: 8, borderRadius: 4, background: i === 5 ? AMBER : accent}} />
              </div>
            );
          })}
        </AbsoluteFill>
      )}

      {/* impact rings */}
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        {[0, 8].map((d, i) => {
          const p = ring(d);
          if (p <= 0 || p >= 1) return null;
          return <circle key={i} cx={cx} cy={cy} r={30 + p * 420} fill="none" stroke={i ? TEAL : BLUE} strokeWidth={2.5 * (1 - p)} opacity={(1 - p) * 0.8} />;
        })}
      </svg>

      {/* title group */}
      <AbsoluteFill style={{transform: `translateY(${-150 * shift}px) scale(${1 - 0.14 * shift})`, transformOrigin: '960px 540px'}}>
        <div style={{position: 'absolute', top: 470, left: 0, right: 0, display: 'flex', justifyContent: 'center', transform: 'translateY(-50%)'}}>
          <Chars text="鸿图体系绘图" frame={f} start={148} stagger={4} size={176} ls="0.05em" sweep={sweep1} />
        </div>
        <div style={{position: 'absolute', top: 604, left: 0, right: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 34, transform: 'translateY(-50%)'}}>
          <Rule p={sloP} w={200} color={TEAL} />
          <div style={{fontFamily: SANS, fontWeight: 400, fontSize: 44, letterSpacing: '0.2em', color: '#CFE2F7', whiteSpace: 'pre',
            clipPath: `inset(-10px ${(1 - sloP) * 100}% -10px 0)`, opacity: prog(f, 176, 188), textShadow: '0 0 14px rgba(76,168,255,0.35)'}}>绘体系之图　展鸿鹄之志</div>
          <Rule p={sloP} w={200} color={TEAL} diamond />
        </div>
        <div style={{position: 'absolute', top: 686, left: 0, right: 0, display: 'flex', justifyContent: 'center', transform: 'translateY(-50%)'}}>
          <div style={{fontFamily: SANS, fontWeight: 300, fontSize: 26, letterSpacing: '0.6em', paddingLeft: '0.6em', color: '#8FB4DC',
            opacity: orgP, transform: `translateY(${(1 - orgP) * 10}px)`}}>{org}</div>
        </div>
      </AbsoluteFill>

      {/* thanks */}
      <div style={{position: 'absolute', top: 790, left: 0, right: 0, display: 'flex', justifyContent: 'center', transform: 'translateY(-50%)'}}>
        <Chars text="感谢观看" frame={f} start={222} stagger={5} size={118} ls="0.16em" sweep={sweep2} glow="rgba(43,212,196,0.6)" />
      </div>
      <div style={{position: 'absolute', top: 886, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
        <Rule p={prog(f, 240, 268)} w={460} color={TEAL} diamond />
      </div>
      <AbsoluteFill style={{background: INK, opacity: 1 - fadeIn}} />
    </Stage>
  );
};
