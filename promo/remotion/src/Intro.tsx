import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {AMBER, BLUE, Backdrop, Chars, Diagram, Rule, SANS, Stage, TEAL, INK, prog, ease} from './common';

export const Intro: React.FC = () => {
  const f = useCurrentFrame();
  const glow = prog(f, 70, 130);
  const sweep = prog(f, 118, 150, (t) => t);
  const subP = prog(f, 104, 130);
  const tagP = prog(f, 138, 168);
  const fade = Math.min(prog(f, 0, 8, (t) => t), 1 - prog(f, 202, 210, (t) => t));
  return (
    <Stage>
      <Backdrop glow={glow} glowY={520} />
      <Diagram start={6} pulseStart={84} />
      <AbsoluteFill style={{alignItems: 'center'}}>
        <div style={{position: 'absolute', top: 478, transform: 'translateY(-50%)'}}>
          <Chars text="鸿图体系绘图" frame={f} start={70} stagger={4} size={176} ls="0.05em" sweep={sweep} />
        </div>
        <div style={{position: 'absolute', top: 618, left: 0, right: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 36, transform: 'translateY(-50%)'}}>
          <Rule p={subP} w={260} color={BLUE} />
          <div style={{fontFamily: SANS, fontWeight: 500, fontSize: 54, letterSpacing: '0.55em', paddingLeft: '0.55em', color: '#8FF0E6',
            opacity: prog(f, 106, 126), transform: `translateY(${(1 - prog(f, 106, 130)) * 18}px)`, textShadow: `0 0 18px rgba(43,212,196,0.5)`}}>使用教程</div>
          <Rule p={subP} w={260} color={BLUE} diamond />
        </div>
        <div style={{position: 'absolute', top: 688, left: 0, right: 0, display: 'flex', justifyContent: 'center', transform: 'translateY(-50%)'}}>
          <div style={{fontFamily: SANS, fontWeight: 300, fontSize: 38, letterSpacing: '0.14em', color: '#C4DAF2', whiteSpace: 'pre',
            opacity: prog(f, 138, 152), clipPath: `inset(-10px ${(1 - tagP) * 100}% -10px 0)`, transform: `translateY(${(1 - tagP) * 8}px)`}}>
            让画图快起来　让图美起来
          </div>
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{background: INK, opacity: 1 - fade}} />
    </Stage>
  );
};
