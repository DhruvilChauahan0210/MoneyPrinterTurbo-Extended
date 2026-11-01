"""Serve a folder to studio.youtube.com so sched.js can fetch the Shorts + meta.json.

Usage: python3 cors_server.py FOLDER [PORT=8799] &     (stop it by PID afterwards)
"""
import functools
import http.server
import sys

folder = sys.argv[1]
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8799


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "https://studio.youtube.com")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def log_message(self, *a):
        pass


http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(H, directory=folder)).serve_forever()
