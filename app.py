#!/usr/bin/env python3
"""Length Extension — real mini-challenge (length-extension)."""
import base64, hashlib, hmac, json, os, re, sqlite3, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, unquote, quote

sys.path.insert(0, "/challenge/_shared")
from fetch_material import fetch_material

CHALLENGE_KEY = os.environ.get("CHALLENGE_KEY", 'merkle-damgard')
_MAT = {}

SECRET = (CHALLENGE_KEY or "").encode()

def md5_mac(data):
    return hashlib.md5(SECRET + data).hexdigest()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/plain", headers=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        data = body if isinstance(body, bytes) else body.encode()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


    def do_GET(self):
        p = urlparse(self.path)
        qs = parse_qs(p.query)
        if p.path == "/flag":
            return self._send(200, _MAT.get("delivery_blob", "") + "\n")
        if p.path == "/meta":
            return self._send(200, f"secret_len={len(SECRET)}\n")
        if p.path == "/profile":
            uid = qs.get("uid", ["1"])[0]
            msg = f"uid={uid}".encode()
            return self._send(200, f"msg={msg.decode()} mac={md5_mac(msg)}\n")
        if p.path == "/get":
            msg = qs.get("msg", [""])[0].encode()
            mac = qs.get("mac", [""])[0]
            if msg == b"uid=1;admin=1" and mac == md5_mac(msg):
                return self._send(200, f"ok; key={CHALLENGE_KEY}\n")
            return self._send(403, "bad mac or msg\n")
        self._send(200, "Length extension: /profile?uid=1  /meta  /get?msg=&mac=  /flag\n")


def main():
    _MAT.update(fetch_material())
    print('Length Extension on :8080')
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

if __name__ == "__main__":
    main()
