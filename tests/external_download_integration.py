"""Real HTTP/API/transfer test; ORBIT_TEST can only download loopback fixtures."""
import hashlib
import http.server
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = bytes(range(256)) * 32
expected_filename = "fixture.ffpfsc"
requests = []


class Provider(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_POST(self):
        from urllib.parse import parse_qs
        assert self.path == "/services/xauthn/?op=login"
        form = parse_qs(self.rfile.read(int(self.headers["Content-Length"])).decode())
        assert form == {"email": ["fixture@example.invalid"], "password": ["fixture-password"]}
        body = json.dumps({"success": True, "values": {"screenname": "Fixture account",
            "cookies": {"logged-in-user": "fixture-user; path=/", "logged-in-sig": "fixture-signature; path=/"}}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        requests.append((self.path, self.headers.get("Range")))
        body = PAYLOAD
        total = len(body) + (1 if self.path == "/wrong-size" else 0)
        match = re.fullmatch(r"bytes=(\d+)-(\d+)", self.headers.get("Range", ""))
        start, end = (int(v) for v in match.groups()) if match else (0, len(body) - 1)
        assert 0 <= start <= end < len(body)
        body = body[start:end + 1]
        self.send_response(206 if match else 200)
        self.send_header("Content-Type", "text/html" if self.path == "/html" else "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Accept-Ranges", "bytes")
        if match:
            self.send_header("Content-Range", f"bytes {start}-{end}/{total}")
        name = "wrong.ffpfsc" if self.path == "/wrong-name" else expected_filename
        self.send_header("Content-Disposition", f'attachment; filename="{name}"')
        if self.path != "/no-identity":
            self.send_header("ETag", '"fixture-identity"')
        self.end_headers()
        self.wfile.write(body)


def main():
    global expected_filename
    provider = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Provider)
    threading.Thread(target=provider.serve_forever, daemon=True).start()
    provider_origin = f"http://127.0.0.1:{provider.server_port}"
    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        port = reserved.getsockname()[1]
    origin = f"http://127.0.0.1:{port}"
    token = ""
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def api(path, body=None, auth=True, headers=None):
        h = {"Content-Type": "application/json"} if body is not None else {}
        if auth and token:
            h["Authorization"] = "Bearer " + token
        h.update(headers or {})
        request = urllib.request.Request(origin + "/api/v1" + path,
            data=json.dumps(body).encode() if body is not None else None, headers=h)
        try:
            response = opener.open(request, timeout=10)
        except urllib.error.HTTPError as response_error:
            response = response_error
        with response:
            return response.status, json.load(response)

    with tempfile.TemporaryDirectory(prefix="orbit-pc-link-") as tmp:
        temp = Path(tmp)
        storage = temp / "storage"
        storage.mkdir()
        env = {**os.environ, "ORBIT_TEST_URL": provider_origin + "/catalog-entry",
            "ORBIT_TEST_SIZE": str(len(PAYLOAD)), "ORBIT_TEST_SOURCE": "vikingfile",
            "ORBIT_TEST_SHA256": hashlib.sha256(PAYLOAD).hexdigest(),
            "ORBIT_TEST_BROWSER_URL": provider_origin + "/provider-page",
            "ORBIT_TEST_ARCHIVE_URL": provider_origin}
        env.pop("ORBIT_TEST_CAPTURE_URL", None)
        with (temp / "server.log").open("w+") as log:
            process = subprocess.Popen([str(ROOT / "build/orbit-test"), "--port", str(port),
                "--state", str(temp / "state"), "--storage", str(storage)],
                cwd=ROOT, env=env, stdout=log, stderr=log)
            try:
                for _ in range(200):
                    if process.poll() is not None:
                        log.seek(0)
                        raise AssertionError(log.read())
                    try:
                        if api("/system")[0] == 200:
                            break
                    except (OSError, ValueError):
                        pass
                    time.sleep(0.05)
                else:
                    raise AssertionError("API did not start")
                assert api("/browser/page?releaseId=missing", auth=False)[0] == 401
                code, session = api("/session")
                assert code == 200
                token = session["token"]
                assert api("/archive-account", auth=False)[0] == 401
                assert api("/archive-account")[1] == {"signedIn": False, "name": "", "busy": False}
                code, account = api("/archive-account", {"action": "sign-in",
                    "email": "fixture@example.invalid", "password": "fixture-password"})
                assert code == 200 and account == {"signedIn": True, "name": "Fixture account", "busy": False}, (code, account)
                saved_account = temp / "state" / "archive-account.json"
                assert saved_account.exists() and "fixture-password" not in saved_account.read_text()
                assert api("/archive-account")[1] == account
                code, account = api("/archive-account", {"action": "sign-out"})
                assert code == 200 and not account["signedIn"] and not saved_account.exists()
                print("PASS 1.3.5 Archive.org sign-in and sign-out with isolated provider fixture")
                assert api("/sources", {"enabled": ["vikingfile"], "acknowledged": True,
                    "noticeVersion": 1})[0] == 200
                _, catalog = api("/catalog")
                release = next(r for r in catalog if r["id"] == "ppsa04029-ffpfsc")
                expected_filename = release["filename"]
                _, drives = api("/storage")
                assert drives
                destination = drives[0]["id"]
                page_path = "/browser/page?releaseId=" + release["id"]
                assert api(page_path) == (200, {"url": provider_origin + "/provider-page"})
                assert api("/browser/page?releaseId=missing")[0] == 400
                assert api(page_path, headers={"Origin": "https://unrelated.example"})[0] == 403
                assert api(page_path, headers={"Sec-Fetch-Site": "cross-site"})[0] == 403
                print("PASS API: pairing, enabled source and origin checks")

                def submit(path):
                    code, status = api("/browser", {"action": "start", "releaseId": release["id"],
                        "storageId": destination, "directUrl": provider_origin + path})
                    assert code == 202, (code, status)
                    for _ in range(200):
                        _, status = api("/browser")
                        if not status["active"]:
                            return status
                        time.sleep(0.025)
                    raise AssertionError("Verification timeout")

                for path in ["/wrong-size", "/wrong-name", "/html", "/no-identity"]:
                    status = submit(path)
                    assert status["state"] == "failed", (path, status)
                    assert api("/downloads")[1] == []
                    print("PASS transfer rejects " + path)
                status = submit("/file")
                assert status["state"] == "queued", status
                for _ in range(400):
                    _, jobs = api("/downloads")
                    assert len(jobs) == 1
                    if jobs[0]["status"] == "complete":
                        break
                    assert jobs[0]["status"] not in ("error", "cancelled"), jobs[0]
                    time.sleep(0.025)
                else:
                    raise AssertionError("Download did not complete")
                files = list(storage.rglob(expected_filename))
                assert len(files) == 1 and files[0].read_bytes() == PAYLOAD
                assert not any(path in ("/provider-page", "/catalog-entry") for path, _ in requests)
                assert any(path == "/file" and byte_range == "bytes=0-0" for path, byte_range in requests)
                assert api("/sources", {"enabled": [], "acknowledged": True, "noticeVersion": 1})[0] == 200
                assert api(page_path)[0] == 400
                print("PASS complete download: external URL, byte probe, checksum and published file")
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    provider.shutdown()


if __name__ == "__main__":
    main()
