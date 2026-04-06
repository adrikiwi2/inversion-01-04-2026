#!/usr/bin/env python3
"""
Servidor local para el Intelligence Engine Dashboard.
Sirve HTML + JSON desde el directorio intelligence/.

Uso: python serve.py [puerto]
Default: http://localhost:8800
"""

import http.server
import json
import os
import sys
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8800
DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(DIR)

DATA_DIR = Path(DIR) / "fetcher" / "data"


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".json": "application/json",
    }

    def do_GET(self):
        # API: list available JSON files in fetcher/data/
        if self.path == "/api/files":
            files = sorted(f.name for f in DATA_DIR.glob("*.json")) if DATA_DIR.exists() else []
            payload = json.dumps(files).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        return super().do_GET()


with http.server.HTTPServer(("", PORT), Handler) as httpd:
    print(f"Intelligence Engine Dashboard")
    print(f"  http://localhost:{PORT}/dashboard.html")
    print(f"  http://localhost:{PORT}/statusPrueba1.html")
    print(f"  API: http://localhost:{PORT}/api/files")
    print(f"  Ctrl+C para parar")
    httpd.serve_forever()
