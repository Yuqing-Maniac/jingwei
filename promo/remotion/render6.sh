#!/bin/bash
cd "$(dirname "$0")"
OUT=/home/claude/video/t6/brand; mkdir -p $OUT
R=/tmp/v6raw; mkdir -p $R
fin(){ ffmpeg -loglevel error -y -i $R/$1_raw.mp4 -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 128k -shortest -movflags +faststart $OUT/$1.mp4; echo "done $1" >> $R/progress.log; }
: > $R/progress.log
npx remotion render src/index.ts IntroV3 $R/intro_v3_raw.mp4 --concurrency=2 --log=error && fin intro_v3
ORG=$(python3 ../../build/brand.py org)   # 机构标识：brand.local.json（不入库）> brand.example.json
npx remotion render src/index.ts OutroV3 $R/outro_v3_raw.mp4 --concurrency=2 --log=error --props="{\"org\":\"$ORG\"}" && fin outro_v3
names=("" 文字成图 "拖拽补充·编队组合" 连线与美化 体系规范 互通与转换 模板与导出)
for i in 1 2 3 4 5 6; do n=$(printf %02d $i)
  npx remotion render src/index.ts Sting $R/sting_${n}_raw.mp4 --concurrency=2 --log=error --props="{\"num\":\"$n\",\"title\":\"${names[$i]}\"}" && fin sting_$n
done
cp /home/claude/video/t5/brand/sting_intro_v3.wav /home/claude/video/t5/brand/sting_outro_v3.wav $OUT/
echo ALL >> $R/progress.log
