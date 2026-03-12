#!/usr/bin/env python3
"""Serve the R0 animation dashboard locally."""

import os
import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8765
DIR = Path(__file__).parent


def main():
    os.chdir(DIR)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"Serving at {url}")
        print("Press Ctrl+C to stop")
        webbrowser.open(url)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
