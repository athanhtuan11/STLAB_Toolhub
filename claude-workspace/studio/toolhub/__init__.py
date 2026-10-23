"""STLAB Toolhub: giao dien web (Flask) cho workspace claude-workspace.

Chay tu thu muc studio: `uv run flask run` (cau hinh trong .flaskenv).
Trang nay MO DUOC CHUONG TRINH tren may, nen:
  - chi nghe 127.0.0.1 va kiem tra Host (chong DNS rebinding);
  - moi POST phai co header X-Studio: 1 (trang web la khong gui duoc header nay -> chong CSRF).
"""
import os
import sys
from pathlib import Path

from flask import Flask, abort, request

# launcher.py nam o thu muc studio (cha cua package nay)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def create_app():
    app = Flask(__name__)
    port = os.environ.get("FLASK_RUN_PORT", "5050")
    allowed = {f"127.0.0.1:{port}", f"localhost:{port}"}

    @app.before_request
    def guard():
        if request.host not in allowed:
            abort(403)
        if request.method == "POST":
            if request.headers.get("X-Studio") != "1":
                abort(403)
            origin = request.headers.get("Origin")
            if origin and origin.split("://", 1)[-1] not in allowed:
                abort(403)

    from .views import bp
    app.register_blueprint(bp)
    return app
