#!/usr/bin/env python3
"""
Servidor local para el Intelligence Engine Dashboard.
Sirve HTML + JSON desde el directorio intelligence/.

Uso: python serve.py [puerto]
Default: http://localhost:8800
"""

import http.server
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8800
DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(DIR)

handler = http.server.SimpleHTTPRequestHandler
handler.extensions_map.update({".json": "application/json"})

with http.server.HTTPServer(("", PORT), handler) as httpd:
    print(f"Intelligence Engine Dashboard")
    print(f"  http://localhost:{PORT}/dashboard.html")
    print(f"  Ctrl+C para parar")
    httpd.serve_forever()
