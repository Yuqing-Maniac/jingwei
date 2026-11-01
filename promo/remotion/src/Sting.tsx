import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {AMBER, BLUE, BRAND, Backdrop, SANS, Stage, TEAL, prog} from './common';
import {Flash, Glitch, Wipe, kick, shakeXY, slam, snap, rnd} from './v3';

export type StingProps = {num: string; title: string};
const grad = (a: string, b: string): React.CSSProperties => ({color: 'transparent', backgroundImage: `linear-gradient(180deg, ${a} 5%, ${b} 100%)`, WebkitBackgroundClip: 'text', backgroundClip: 'text'});

export const Sting: React.FC<StingProps> = ({num, title}) => {
  const f = useCurrentFrame();
  const idx = parseInt(num, 10);
  const [sx, sy] = shakeXY(f, [5], 9);
  const sN = slam(f, 3);
  const gOut = prog(f, 24, 32, (t) => t) * (f < 33 ? 1 : 0);
  const gIn = f < 8 ? 0.8 * (1 - f / 8) : 0;
  const g = Math.max(gIn, gOut * 0.9, kick(f, 5, 5) * 0.7);
  const len = Array.from(title).length;
  const tSize = len <= 4 ? 180 : len <= 6 ? 160 : 132;
  const tp = prog(f, 5, 15);
  const tS = snap(f, 5);
  const lineP = prog(f, 4, 16);
  const cam = 1 + 0.05 * prog(f, 0, 36, (t) => t) + 0.03 * kick(f, 5, 8);
  const Num = (tint?: string) => (
    <div style={{fontFamily: BRAND, fontSize: 440, lineHeight: 1, letterSpacing: '0.02em', ...(tint ? {color: tint} : grad('#FFFFFF', '#3F9FF2')),
      ...(tint ? {} : {filter: 'drop-shadow(0 0 30px rgba(76,168,255,0.6))'})}}>{num}</div>
  );
  const Ttl = (tint?: string) => (
    <div style={{fontFamily: BRAND, fontSize: tSize, lineHeight: 1.1, whiteSpace: 'pre', letterSpacing: '0.04em', ...(tint ? {color: tint} : grad('#FFFFFF', '#BFE2FF')),
      ...(tint ? {} : {filter: 'drop-shadow(0 0 22px rgba(76,168,255,0.45))'})}}>{title}</div>
  );
  return (
    <Stage>
      <div style={{position: 'absolute', inset: 0, transform: `translate(${sx}px,${sy}px) scale(${cam})`}}>
        <Backdrop glow={0.7} glowY={540} />
        <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
          <div style={{position: 'absolute', left: 150, top: 200, display: 'flex', alignItems: 'center', gap: 18, opacity: prog(f, 3, 10)}}>
            <div style={{width: 70 * lineP, height: 3, background: AMBER, boxShadow: `0 0 12px ${AMBER}`}} />
            <div style={{fontFamily: SANS, fontWeight: 500, fontSize: 28, letterSpacing: '0.35em', color: '#8FB4DC'}}>{`CHAPTER ${num} / 06`}</div>
          </div>
          <div style={{display: 'flex', alignItems: 'center', gap: 56}}>
            <div style={{transform: `scale(${1 + (1 - sN) * 0.7})`, opacity: f >= 3 ? 1 : 0}}>
              <Glitch f={f} g={g}>{Num}</Glitch>
            </div>
            <div style={{width: 8, height: 300 * lineP, background: `linear-gradient(180deg, ${TEAL}, ${BLUE})`, boxShadow: `0 0 18px ${BLUE}`, borderRadius: 4}} />
            <div style={{clipPath: `inset(-20px ${(1 - tp) * 100}% -20px 0)`, transform: `translateX(${(1 - tS) * 160}px)`, opacity: f >= 5 ? 1 : 0}}>
              <Glitch f={f + 3} g={g}>{Ttl}</Glitch>
            </div>
          </div>
          <div style={{position: 'absolute', bottom: 170, display: 'flex', gap: 22}}>
            {[1, 2, 3, 4, 5, 6].map((n) => {
              const on = n === idx, p = snap(f, 8 + n);
              return <div key={n} style={{width: on ? 74 : 22, height: 12, borderRadius: 6, transform: `scaleX(${Math.max(0, p)})`, background: on ? AMBER : n < idx ? TEAL : '#27456f',
                boxShadow: on ? `0 0 16px ${AMBER}` : undefined, opacity: n < idx ? 0.8 : 1}} />;
            })}
          </div>
        </AbsoluteFill>
      </div>
      <Flash f={f} t={5} peak={0.22} dur={6} color="#DFF1FF" />
      <Wipe f={f} a={0} b={9} mode="reveal" />
      <Wipe f={f} a={26} b={35} mode="cover" />
    </Stage>
  );
};
