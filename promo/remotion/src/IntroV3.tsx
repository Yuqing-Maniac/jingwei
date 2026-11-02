import React from 'react';
import {AbsoluteFill, interpolate, Img, staticFile} from 'remotion';
import {useCurrentFrame} from 'remotion';
import {AMBER, BLUE, Backdrop, Diagram, SANS, Stage, TEAL, prog} from './common';
import {Flash, Glitch, Impact, ScanLine, Sweep, TitleTxt, Wipe, kick, shakeXY, slam, snap} from './v3';

const T = 42, TA = 78, TB = 88;
export const IntroV3: React.FC = () => {
  const f = useCurrentFrame();
  const [sx, sy] = shakeXY(f, [T, TA, TB], 11);
  const cam = 1 + 0.1 * prog(f, 0, 160, (t) => t) + 0.04 * kick(f, T, 12) + 0.018 * kick(f, TA, 8) + 0.018 * kick(f, TB, 8);
  const dim = prog(f, 30, 46);
  const ps = slam(f, T);
  const tScale = 1 + (1 - ps) * 1.0;
  const g = Math.max(kick(f, T, 8), f < 5 ? 0.9 : 0, prog(f, 156, 166, (t) => t) * 0.9 * (f < 168 ? 1 : 0)) ;
  const sweepP = prog(f, 104, 130, (t) => t);

  const piece = (t: number, dir: number, text: string, color: string) => {
    const s = snap(f, t);
    const p = prog(f, t, t + 7);
    return (
      <div style={{fontFamily: SANS, fontWeight: 500, fontSize: 72, letterSpacing: "0.12em", color, whiteSpace: 'pre', opacity: p,
        transform: `translateX(${(1 - s) * dir * 420}px) scale(${1 + (1 - s) * 0.12})`, filter: `blur(${(1 - Math.min(1, s)) * 8}px)`,
        textShadow: `0 0 ${18 + 30 * kick(f, t, 10)}px ${color}88`}}>{text}</div>
    );
  };
  const underP = prog(f, TB + 4, TB + 16);
  return (
    <Stage>
      <div style={{position: 'absolute', inset: 0, transform: `translate(${sx}px,${sy}px) scale(${cam})`, transformOrigin: '50% 48%'}}>
        <Backdrop glow={prog(f, T - 4, T + 20)} glowY={500} />
        <div style={{position: 'absolute', inset: 0, opacity: 1 - 0.72 * dim}}>
          <Diagram start={1} speed={3.4} pulseStart={20} />
        </div>
        <ScanLine p={prog(f, 1, 18, (t) => t)} />
        <AbsoluteFill style={{alignItems: 'center'}}>
          {f >= T && (
            <div style={{position: 'absolute', top: 470, transform: `translateY(-50%) scale(${tScale})`, opacity: Math.min(1, (f - T + 1) / 2)}}>
              <div style={{display: 'flex', alignItems: 'center', gap: 52}}>
                  <Img src={staticFile('logo.svg')} style={{width: 176, height: 176, filter: 'drop-shadow(0 10px 30px rgba(10,40,90,0.8)) drop-shadow(0 0 24px rgba(76,168,255,0.45))'}} />
                  <div style={{position: 'relative'}}>
                    <Glitch f={f} g={g}>{(tint) => <TitleTxt text="经纬织图" size={200} tint={tint} ls="0.08em" />}</Glitch>
                    <Sweep text="经纬织图" size={200} p={sweepP} ls="0.08em" />
                  </div>
                </div>
            </div>
          )}
          <div style={{position: 'absolute', top: 640, left: 0, right: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 56, transform: 'translateY(-50%)'}}>
            {f >= TA && piece(TA, -1, '让画图快起来', '#CFE4FA')}
            {f >= TA && <div style={{width: 14, height: 14, background: AMBER, transform: `rotate(45deg) scale(${snap(f, TA + 3)})`, boxShadow: `0 0 16px ${AMBER}`}} />}
            {f >= TB && piece(TB, 1, '让图美起来', '#8FF0E6')}
          </div>
          <div style={{position: 'absolute', top: 700, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
            <div style={{width: 760 * underP, height: 3, background: `linear-gradient(90deg, transparent, ${BLUE}, ${TEAL}, transparent)`, boxShadow: `0 0 14px ${BLUE}`}} />
          </div>
        </AbsoluteFill>
        <Impact f={f} t={T} cx={960} cy={470} />
        <Impact f={f} t={TA} cx={700} cy={640} n={10} r0={60} big={0.35} />
        <Impact f={f} t={TB} cx={1230} cy={640} n={10} r0={60} big={0.35} />
      </div>
      <Flash f={f} t={0} peak={1} dur={6} />
      <Flash f={f} t={T} peak={0.75} dur={8} color="#DFF1FF" />
      <Flash f={f} t={TA} peak={0.18} dur={5} />
      <Flash f={f} t={TB} peak={0.18} dur={5} />
      <Wipe f={f} a={152} b={172} mode="cover" />
    </Stage>
  );
};
