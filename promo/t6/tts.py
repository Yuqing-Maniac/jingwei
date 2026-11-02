"""MiniMax TTS for t6. Key from env MM_KEY only (never stored)."""
import json, os, sys, urllib.request, concurrent.futures as cf
K=os.environ['MM_KEY']; S=json.load(open('/home/claude/video/t6/script.json',encoding='utf-8'))
TTS_TEXT={'035a':'第四招，格式互通。老图不用重画，PPT、Visio、draw dot io 文件直接打开，自动识别分层和连线。'}
def one(s):
    out=f"/home/claude/video/t6/audio/{s['id']}.mp3"
    if os.path.exists(out) and '--force' not in sys.argv: return s['id'],'skip'
    body={"model":"speech-02-hd","text":TTS_TEXT.get(s['id'],s['text']),"stream":False,
      "voice_setting":{"voice_id":"presenter_male","speed":1.12,"vol":1.0,"pitch":0,"emotion":"happy"},
      "audio_setting":{"sample_rate":32000,"bitrate":128000,"format":"mp3","channel":1}}
    req=urllib.request.Request('https://api.minimax.io/v1/t2a_v2',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+K,'Content-Type':'application/json'})
    for k in range(3):
        try:
            r=json.loads(urllib.request.urlopen(req,timeout=120).read()); break
        except Exception as e: err=str(e)
    else: return s['id'],'ERR '+err
    if r.get('base_resp',{}).get('status_code')!=0: return s['id'],'ERR '+json.dumps(r.get('base_resp'))
    open(out,'wb').write(bytes.fromhex(r['data']['audio'])); return s['id'],'ok'
with cf.ThreadPoolExecutor(6) as ex:
    for i,st in ex.map(one,S): print(i,st)
