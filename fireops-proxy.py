#!/usr/bin/env python3
"""
FireOps KML Proxy Server
------------------------
Fetches the MONITOR KML feed server-side (no CORS issues)
and serves it to the FireOps HTML app running in your browser.

Usage:
    python3 fireops-proxy.py

Then open: http://localhost:8765
The proxy will be available at: http://localhost:8765/kml
"""

import http.server
import urllib.request
import urllib.error
import os
import json
from pathlib import Path

PORT = 8765
KML_URL = "https://nexe.online/api/position/kml/update?api_key=c1e5ab04-9891-4c3c-8bcf-5912f861bbe8"
HTML_FILE = "wildfire-resource-manager.html"

class ProxyHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"  {self.address_string()} → {format % args}")

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        # Serve the KML proxy endpoint
        if self.path == "/kml" or self.path.startswith("/kml?"):
            self.serve_kml()
        # Serve the main HTML app
        elif self.path == "/" or self.path == "/index.html":
            self.serve_html()
        # Health check
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "proxy": "fireops"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def serve_kml(self):
        try:
            req = urllib.request.Request(
                KML_URL,
                headers={"User-Agent": "FireOps/1.0 KML Proxy"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                content_type = resp.headers.get("Content-Type", "application/vnd.google-earth.kml+xml")

            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.google-earth.kml+xml; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_cors_headers()
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)
            print(f"  ✓ KML fetched — {len(data)} bytes")

        except urllib.error.URLError as e:
            print(f"  ✗ KML fetch failed: {e}")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(f"KML fetch failed: {e}".encode())

        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            self.send_response(500)
            self.end_headers()

    def serve_html(self):
        html_path = Path(__file__).parent / HTML_FILE
        if not html_path.exists():
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"HTML file not found. Make sure wildfire-resource-manager.html is in the same folder.")
            return
        data = html_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    print()
    print("  🔥 FireOps KML Proxy Server")
    print("  ─────────────────────────────────────────")
    print(f"  App URL   →  http://localhost:{PORT}")
    print(f"  KML Proxy →  http://localhost:{PORT}/kml")
    print(f"  Press Ctrl+C to stop")
    print()

    server = http.server.HTTPServer(("localhost", PORT), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
