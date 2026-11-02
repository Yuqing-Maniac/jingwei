import http.server, json, sys, os
D=os.path.dirname(os.path.abspath(__file__))
class H(http.server.BaseHTTPRequestHandler):
    def cors(self):
        self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Headers','*'); self.send_header('Access-Control-Allow-Methods','POST, OPTIONS')
    def do_OPTIONS(self): self.send_response(204); self.cors(); self.end_headers()
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0)); body=json.loads(self.rfile.read(n))
        msgs=body['messages']; open(os.path.join(D,'last_req.json'),'w',encoding='utf-8').write(json.dumps(body,ensure_ascii=False,indent=1))
        u=msgs[-1]['content']
        if '连通' in u: out='连通'
        else:
            p=os.path.join(D,'reply.txt'); out=open(p,encoding='utf-8').read() if os.path.exists(p) else '# 占位\n## 甲\n- 一、二\n## 连接\n- 一 -> 二'
        r=json.dumps({'choices':[{'message':{'role':'assistant','content':out}}]},ensure_ascii=False).encode()
        self.send_response(200); self.cors(); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(r))); self.end_headers(); self.wfile.write(r)
    def log_message(self,*a): pass
http.server.HTTPServer(('127.0.0.1',8765),H).serve_forever()
