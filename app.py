import json, os, re, secrets, time, urllib.error, urllib.parse, urllib.request
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))
socketio = SocketIO(app, cors_allowed_origins=None)
SEND_LOG = {}

@app.after_request
def security_headers(response):
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.get("/")
def index():
    room = request.args.get("invite", "")[:120]
    return render_template(
        "index.html",
        invite_room=room,
        invite_role="device" if room else "",
        supabase_url=os.environ.get("SUPABASE_URL", "").rstrip("/"),
        supabase_anon_key=os.environ.get("SUPABASE_ANON_KEY", ""),
    )

@app.post("/api/invitations")
def create_invitation():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    if len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return jsonify(error="To‘g‘ri email manzilini kiriting."), 400

    project_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    secret_key = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    anon_key = os.environ.get("SUPABASE_ANON_KEY")
    base_url = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
    if not project_url or not secret_key or not anon_key or not base_url:
        return jsonify(error="Supabase sozlanmagan. SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SECRET_KEY va PUBLIC_BASE_URL kerak."), 503
    if not base_url.startswith("https://"):
        return jsonify(error="PUBLIC_BASE_URL telefon ochadigan ommaviy HTTPS manzili bo‘lishi kerak."), 503

    now = time.time()
    ip = request.remote_addr or "unknown"
    for key, limit in (("ip:" + ip, 5), ("email:" + email, 3)):
        recent = [t for t in SEND_LOG.get(key, []) if now - t < 3600]
        if len(recent) >= limit:
            return jsonify(error="Taklif yuborish limiti tugadi. Keyinroq urinib ko‘ring."), 429
        SEND_LOG[key] = recent

    room = secrets.token_urlsafe(32)
    redirect_to = base_url + "/?invite=" + urllib.parse.quote(room, safe="")
    endpoint = project_url + "/auth/v1/invite?" + urllib.parse.urlencode({"redirect_to": redirect_to})
    payload = json.dumps({"email": email, "data": {"purpose": "camera_microphone_consent"}}).encode("utf-8")
    req = urllib.request.Request(endpoint, data=payload, method="POST")
    req.add_header("apikey", secret_key)
    req.add_header("Authorization", "Bearer " + secret_key)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status not in (200, 201):
                return jsonify(error="Supabase email taklifini yubora olmadi."), 502
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        app.logger.warning("Supabase invitation failed (%s): %s", exc.code, detail[:500])
        return jsonify(error="Email yuborilmadi. Supabase SMTP, email shabloni va ruxsat etilgan redirect manzilini tekshiring."), 502
    except Exception:
        app.logger.exception("Supabase invitation failed")
        return jsonify(error="Supabase bilan ulanish amalga oshmadi. Sozlamalarni tekshiring."), 502

    for key in ("ip:" + ip, "email:" + email):
        SEND_LOG.setdefault(key, []).append(now)
    return jsonify(room=room, message="Taklif emailga yuborildi. Qabul qiluvchi havolani ochib, kamera/mikrofon so‘rovini o‘zi tasdiqlashi kerak.")

@socketio.on("join")
def handle_join(data):
    room = str(data.get("room", "")).strip()[:120]
    role = data.get("role")
    if not room or role not in {"device", "viewer"}:
        return
    join_room(room)
    socketio.emit("joined", {"role": role}, to=room)

@socketio.on("signal")
def handle_signal(data):
    room = str(data.get("room", "")).strip()[:120]
    kind = data.get("kind")
    if kind not in {"request", "accepted", "declined", "offer", "answer", "ice", "stop"}:
        return
    payload = {"kind": kind, "from": request.sid, "data": data.get("data")}
    socketio.emit("signal", payload, to=room, include_self=False)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
