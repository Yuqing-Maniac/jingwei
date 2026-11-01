import React from 'react';
import {Composition} from 'remotion';
import {Intro} from './Intro';
import {Outro} from './Outro';
import {IntroV3} from './IntroV3';
import {OutroV3} from './OutroV3';
import {Sting} from './Sting';
import {PainV4, TitleV4, StingV4, IconWallV4, OutroV4} from './v4';
import {TitleV5, StingV5, OutroV5} from './v5';
export const Root: React.FC = () => (
  <>
    <Composition id="Intro" component={Intro} durationInFrames={210} fps={30} width={1920} height={1080} />
    <Composition id="Outro" component={Outro} durationInFrames={300} fps={30} width={1920} height={1080} />
    <Composition id="IntroV3" component={IntroV3} durationInFrames={180} fps={30} width={1920} height={1080} />
    <Composition id="OutroV3" component={OutroV3} durationInFrames={240} fps={30} width={1920} height={1080} />
    <Composition id="Sting" component={Sting} durationInFrames={36} fps={30} width={1920} height={1080} defaultProps={{num: '01', title: '文字成图'}} />
    <Composition id="PainV4" component={PainV4} durationInFrames={408} fps={30} width={1920} height={1080} />
    <Composition id="TitleV4" component={TitleV4} durationInFrames={180} fps={30} width={1920} height={1080} />
    <Composition id="StingV4" component={StingV4} durationInFrames={39} fps={30} width={1920} height={1080} defaultProps={{num: '01', title: '文字成图·一键美化'}} />
    <Composition id="IconWallV4" component={IconWallV4} durationInFrames={279} fps={30} width={1920} height={1080} />
    <Composition id="OutroV4" component={OutroV4} durationInFrames={585} fps={30} width={1920} height={1080} />
    <Composition id="TitleV5" component={TitleV5} durationInFrames={180} fps={30} width={1920} height={1080} />
    <Composition id="StingV5" component={StingV5} durationInFrames={39} fps={30} width={1920} height={1080} defaultProps={{num: '01', title: '文字成图·一键美化', total: 6}} />
    <Composition id="OutroV5" component={OutroV5} durationInFrames={585} fps={30} width={1920} height={1080} />
  </>
);
