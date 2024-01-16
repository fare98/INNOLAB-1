from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from orion_helper import fetch_data_from_orion

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        url_path = self.path

        if url_path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())

        elif url_path == '/data':
            orion_url = 'http://localhost:1026/v2/entities'
            data = fetch_data_from_orion(orion_url)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print('Starting server at http://localhost:8000')
    httpd.serve_forever()
