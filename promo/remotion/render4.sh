#!/bin/bash
cd "$(dirname "$0")"
OUT=/home/claude/video/t4/brand; mkdir -p $OUT
R=/tmp/claude-0/-home-claude/4a98c7fc-ad86-519e-b225-277215eac05a/scratchpad/v4raw; mkdir -p $R
fin(){ ffmpeg -loglevel error -y -i $R/$1_raw.mp4 -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 128k -shortest -movflags +faststart $OUT/$1.mp4; echo "done $1" >> $R/progress.log; }
rr(){ npx remotion render src/index.ts $1 $R/$2_raw.mp4 --concurrency=2 --log=error --codec=h264 --pixel-format=yuv420p --crf=16 ${3:+--props="$3"} && fin $2; }
: > $R/progress.log
rr TitleV4 title_v4
rr StingV4 sting_v4_01 '{"num":"01","title":"文字成图·一键美化","sub":"","isNew":false}'
rr StingV4 sting_v4_02 '{"num":"02","title":"参照生成","sub":"好图一张，同款一套","isNew":true}'
rr StingV4 sting_v4_03 '{"num":"03","title":"三格式互通","sub":"PPT · Visio · draw.io","isNew":true}'
rr StingV4 sting_v4_04 '{"num":"04","title":"两大视图族","sub":"11 种规范视图 · 规范检查","isNew":false}'
rr StingV4 sting_v4_05 '{"num":"05","title":"拟物图标库","sub":"三百多个 · 编队组合","isNew":false}'
rr PainV4 pain_v4
rr IconWallV4 iconwall_v4
rr OutroV4 outro_v4
echo ALL >> $R/progress.log
