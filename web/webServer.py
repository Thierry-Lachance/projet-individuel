from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

class Serv(BaseHTTPRequestHandler):
    
    def do_GET(self):
        requested_path = urlparse(self.path).path
        if requested_path == '/':
            requested_path = '/index.html'

        file_path = Path(__file__).parent / requested_path.lstrip('/')
        try:
            file_to_open = file_path.read_text(encoding='utf-8')
            self.send_response(200)
        except (FileNotFoundError, IsADirectoryError):
            file_to_open = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))