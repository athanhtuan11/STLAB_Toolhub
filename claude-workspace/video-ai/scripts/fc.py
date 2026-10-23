"""Phien FilmCraft chay nen (khong mo cua so) qua MCP stdio cua filmcraft-cli. Chi thu vien chuan.

    with FilmCraft() as fc:
        fc.run("file.newSequence", name="reel", width=1080, height=1920, fps=30)
        print(fc.sequence())

Moi lenh FilmCraft la mot "command" (xem `filmcraft-cli commands`); run() tra ve ket qua JSON cua lenh.
"""
import json
import os
import queue
import subprocess
import threading

FC_CLI = os.environ.get("FILMCRAFT_CLI", r"C:\Program Files\FilmCraft\filmcraft-cli.exe")
TICKS = 254016000000  # tick moi giay (FilmCraft)


def ticks(seconds):
    return int(round(seconds * TICKS))


class FilmCraftError(RuntimeError):
    pass


class FilmCraft:
    def __init__(self, project=None, timeout=600):
        args = [FC_CLI, "mcp"] + (["--project", str(project)] if project else [])
        self.p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.q = queue.Queue()
        threading.Thread(target=lambda: [self.q.put(ln) for ln in self.p.stdout], daemon=True).start()
        self.timeout, self._id = timeout, 0
        self._rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                 "clientInfo": {"name": "stlab-video-ai", "version": "0.1"}})
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _send(self, obj):
        self.p.stdin.write((json.dumps(obj) + "\n").encode("utf-8"))
        self.p.stdin.flush()

    def _rpc(self, method, params):
        self._id += 1
        self._send({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params})
        while True:
            try:
                msg = json.loads(self.q.get(timeout=self.timeout))
            except queue.Empty:
                raise FilmCraftError(f"FilmCraft khong tra loi {method} sau {self.timeout} s")
            if msg.get("id") == self._id:
                if "error" in msg:
                    raise FilmCraftError(str(msg["error"]))
                return msg["result"]

    def tool(self, name, **args):
        res = self._rpc("tools/call", {"name": name, "arguments": args})
        texts = [c.get("text", "") for c in res.get("content", []) if c.get("type") == "text"]
        out = res.get("structuredContent")
        if out is None and texts:
            try:
                out = json.loads(texts[0])
            except ValueError:
                out = texts[0]
        if res.get("isError"):
            raise FilmCraftError(f"{name} {args}: {' '.join(texts)[:500]}")
        return out

    def run(self, command_id, **params):
        """Chay 1 lenh FilmCraft (undo duoc). Tra ve ket qua cua lenh."""
        return self.tool("command_run", id=command_id, params=params)

    def batch(self, steps, stop_on_error=True):
        return self.tool("command_batch", steps=steps, stop_on_error=stop_on_error)

    def project(self):
        return self.tool("project_inspect")

    def sequence(self):
        return self.tool("sequence_inspect")

    def frame_png(self, seconds):
        res = self._rpc("tools/call", {"name": "render_frame", "arguments": {"seconds": seconds}})
        for c in res.get("content", []):
            if c.get("type") == "image":
                import base64
                return base64.b64decode(c["data"])
        raise FilmCraftError("render_frame khong tra ve anh")

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=10)
        except Exception:
            self.p.kill()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()
