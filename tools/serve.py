from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os, webbrowser
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT / 'app')
port = 7070
print(f'SIM EARTH 7.07 serving on http://localhost:{port}/')
try: webbrowser.open(f'http://localhost:{port}/')
except Exception: pass
ThreadingHTTPServer(('127.0.0.1', port), SimpleHTTPRequestHandler).serve_forever()
