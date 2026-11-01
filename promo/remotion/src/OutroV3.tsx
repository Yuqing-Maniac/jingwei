import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {useCurrentFrame} from 'remotion';
import {AMBER, BLUE, BRAND, Backdrop, Chars, Diagram, Rule, SANS, Stage, TEAL, INK, inout, lerp, prog} from './common';
import {Flash, Glitch, Impact, Sweep, TitleTxt, Wipe, kick, shakeXY, slam, snap} from './v3';

const KW = ['绿色', '离线', '免费', '高效', '好用', '普惠'];
const KT = [16, 26, 36, 46, 56, 66];
const CW = 230, CG = 24, CH = 124, CY = 560;
const C0 = 84, C1 = 104, S = 102, SL = 130;

export const OutroV3: React.FC<{org?: string}> = ({org = '经纬织图开发组'}) => {
  const f = useCurrentFrame();
  const cx = 960, cy = 470;
  const cc = prog(f, C0, C1, inout);
  const totalW = 6 * CW + 5 * CG;
  const x0 = 960 - totalW / 2 + CW / 2;
  const shift = prog(f, 124, 144, inout);
  const [sx, sy] = shakeXY(f, [...KT, S, SL], 7);
  const base = f < S ? 1 + 0.07 * prog(f, 0, S, (t) => t) : 1.07 - 0.07 * prog(f, S, 200);
  const cam = base + 0.045 * kick(f, S, 12) + 0.012 * KT.reduce((a, t) => a + kick(f, t, 6), 0) + 0.015 * kick(f, SL, 8);
  const keepChips = 1 - prog(cc, 0.55, 1, (t) => t);
  const ps = slam(f, S);
  const tScale = 1 + (1 - ps) * 0.95;
  const g = Math.max(kick(f, S, 8), 0);
  const sweep1 = prog(f, 150, 180, (t) => t);
  const sloP = prog(f, SL, SL + 14);
  const orgP = prog(f, 152, 170);
  const inCover = prog(f, 0, 8, (t) => t);
  return (
    <Stage>
      <div style={{position: 'absolute', inset: 0, transform: `translate(${sx}px,${sy}px) scale(${cam})`, transformOrigin: '50% 50%'}}>
        <Backdrop glow={prog(f, S - 6, S + 30) * (1 - 0.3 * shift)} glowY={lerp(470, 400, shift)} />
        <div style={{position: 'absolute', inset: 0, opacity: 0.5}}>
          <Diagram start={2} speed={3} pulseStart={24} conv={{c0: C0, c1: C1, cx, cy}} />
        </div>

        {f < C1 && (
          <AbsoluteFill>
            {KW.map((k, i) => {
              if (f < KT[i]) return null;
              const s = snap(f, KT[i]);
              const flash = kick(f, KT[i], 14);
              const x = x0 + i * (CW + CG);
              const from = i % 2 === 0 ? -1 : 1;
              const px = lerp(x, cx, cc), py = lerp(CY, cy, cc) + (1 - s) * from * 190;
              const accent = i % 2 === 0 ? BLUE : TEAL;
              const op = Math.min(1, (f - KT[i] + 1) / 3) * keepChips;
              return (
                <div key={i} style={{position: 'absolute', left: px - CW / 2, top: py - CH / 2, width: CW, height: CH, opacity: op,
                  transform: `scale(${(1 + (1 - s) * 0.55) * (1 - 0.8 * cc)})`, borderRadius: 18,
                  background: `linear-gradient(180deg, rgba(${flash > 0.3 ? '40,90,160' : '16,38,76'},0.96), rgba(8,22,46,0.96))`, border: `2.5px solid ${accent}`,
                  boxShadow: `0 0 ${24 + flash * 60}px ${accent}${flash > 0.25 ? 'cc' : '55'}, inset 0 0 22px ${accent}22`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: BRAND, fontSize: 64, letterSpacing: '0.12em', paddingLeft: '0.12em', color: '#F2F8FF',
                  textShadow: `0 0 16px ${accent}99`}}>
                  {k}
                  <div style={{position: 'absolute', top: 10, left: 16, fontFamily: SANS, fontSize: 16, letterSpacing: 2, color: accent, opacity: 0.9}}>{`0${i + 1}`}</div>
                  <div style={{position: 'absolute', right: 16, bottom: 14, width: 9, height: 9, borderRadius: 5, background: i === 5 ? AMBER : accent}} />
                </div>
              );
            })}
          </AbsoluteFill>
        )}
        {KW.map((_, i) => f >= KT[i] && f < KT[i] + 16 && (
          <Impact key={i} f={f} t={KT[i]} cx={x0 + i * (CW + CG)} cy={CY} n={8} r0={50} big={0.25} />
        ))}

        <AbsoluteFill style={{transform: `translateY(${-150 * shift}px) scale(${1 - 0.14 * shift})`, transformOrigin: '960px 540px'}}>
          {f >= S && (
            <div style={{position: 'absolute', top: 470, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
              <div style={{transform: `translateY(-50%) scale(${tScale})`, opacity: Math.min(1, (f - S + 1) / 2)}}>
                <div style={{display: 'flex', alignItems: 'center', gap: 52}}>
                  <Img src={staticFile('logo.svg')} style={{width: 168, height: 168, filter: 'drop-shadow(0 10px 30px rgba(10,40,90,0.8)) drop-shadow(0 0 24px rgba(76,168,255,0.45))'}} />
                  <div style={{position: 'relative'}}>
                    <Glitch f={f} g={g}>{(tint) => <TitleTxt text="经纬织图" size={192} tint={tint} ls="0.08em" />}</Glitch>
                    <Sweep text="经纬织图" size={192} p={sweep1} ls="0.08em" />
                  </div>
                </div>
              </div>
            </div>
          )}
          <div style={{position: 'absolute', top: 606, left: 0, right: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 34, transform: 'translateY(-50%)'}}>
            <Rule p={sloP} w={200} color={TEAL} />
            {f >= SL && <Chars text="把时间还给思考" frame={f} start={SL} stagger={2.4} dur={12} rise={34} size={64} family={SANS} weight={500} color="#DCEBFF" ls="0.2em" glow="rgba(76,168,255,0.4)" />}
            <Rule p={sloP} w={200} color={TEAL} diamond />
          </div>
          <div style={{position: 'absolute', top: 700, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
            <div style={{fontFamily: SANS, fontWeight: 300, fontSize: 28, letterSpacing: '0.6em', paddingLeft: '0.6em', color: '#8FB4DC',
              opacity: orgP, transform: `translateY(${(1 - orgP) * 12}px)`}}>{org}</div>
          </div>
        </AbsoluteFill>
        <Impact f={f} t={S} cx={cx} cy={cy} big={1.1} />
        <Impact f={f} t={SL} cx={960} cy={440} n={12} r0={80} big={0.4} />
      </div>
      <Flash f={f} t={S} peak={0.8} dur={9} color="#DFF1FF" />
      {KT.map((t) => <Flash key={t} f={f} t={t} peak={0.1} dur={4} />)}
      <Wipe f={f} a={0} b={10} mode="reveal" />
    </Stage>
  );
};
