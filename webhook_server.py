from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            payload = body.decode('utf-8')
        except Exception:
            payload = str(body)
        print("[WEBHOOK] Path:", self.path)
        print("[WEBHOOK] Headers:", dict(self.headers))
        print("[WEBHOOK] Body:", payload)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def log_message(self, format, *args):
        # Silencia logs padrões
        return

def main():
    server = HTTPServer(('0.0.0.0', 9000), Handler)
    print('Webhook fake ouvindo em http://localhost:9000/webhook', flush=True)
    server.serve_forever()

if __name__ == '__main__':
    main()