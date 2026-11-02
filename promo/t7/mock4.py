import http.server, json, os, time
D=os.path.dirname(os.path.abspath(__file__))
class H(http.server.BaseHTTPRequestHandler):
    def cors(self):
        self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Headers','*'); self.send_header('Access-Control-Allow-Methods','POST, OPTIONS')
    def do_OPTIONS(self): self.send_response(204); self.cors(); self.end_headers()
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0)); body=json.loads(self.rfile.read(n))
        u=body['messages'][-1]['content']
        out='连通' if '连通' in u else open(os.path.join(D,'reply.txt'),encoding='utf-8').read()
        time.sleep(float(os.environ.get('MOCK_DELAY','1.6')) if '连通' not in u else 0.3)
        r=json.dumps({'choices':[{'message':{'role':'assistant','content':out}}]},ensure_ascii=False).encode()
        self.send_response(200); self.cors(); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(r))); self.end_headers(); self.wfile.write(r)
    def log_message(self,*a): pass
http.server.ThreadingHTTPServer(('127.0.0.1',8766),H).serve_forever()
