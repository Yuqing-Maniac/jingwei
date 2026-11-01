#!/bin/bash
cd "$(dirname "$0")"
OUT=/home/claude/video/t7/brand; mkdir -p $OUT
R=/tmp/claude-0/v7raw; mkdir -p $R
fin(){ ffmpeg -loglevel error -y -i $R/$1_raw.mp4 -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 128k -shortest -movflags +faststart $OUT/$1.mp4; echo "done $1" >> $R/progress.log; }
rr(){ npx remotion render src/index.ts $1 $R/$2_raw.mp4 --concurrency=2 --log=error --codec=h264 --pixel-format=yuv420p --crf=16 ${3:+--props="$3"} && fin $2; }
: > $R/progress.log
rr TitleV5 title_v5
rr StingV5 sting_v5_01 '{"num":"01","title":"文字成图·一键美化","sub":"","isNew":false,"total":6}'
rr StingV5 sting_v5_02 '{"num":"02","title":"智能连线","sub":"中点出入 · 自动避障 · 拖动吸附","isNew":true,"total":6}'
rr StingV5 sting_v5_03 '{"num":"03","title":"参照生成","sub":"好图一张，同款一套","isNew":false,"total":6}'
rr StingV5 sting_v5_04 '{"num":"04","title":"格式互通","sub":"Visio 转 PPT · 字号不走样","isNew":true,"total":6}'
rr StingV5 sting_v5_05 '{"num":"05","title":"两大视图族","sub":"11 种规范视图 · 规范检查","isNew":false,"total":6}'
rr StingV5 sting_v5_06 '{"num":"06","title":"拟物图标库","sub":"三百多个 · 编队组合","isNew":false,"total":6}'
rr OutroV5 outro_v5
echo ALL >> $R/progress.log
