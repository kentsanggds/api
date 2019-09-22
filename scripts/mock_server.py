import BaseHTTPServer


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('VERIFIED')


def main():
    httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 5005), Handler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
