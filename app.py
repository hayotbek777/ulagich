import os, secrets, time, urllib.parse, urllib.request, base64
from flask import Flask, render_template, request, jsonify, abort
from flask_socketio import SocketIO, join_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))
socketio = SocketIO(app, cors_allowed_origins=None)
INVITES = {}
SEND_LOG = {}
INVITE_TTL = 600

@app.get("/")
def index():
    return render_template("index.html", invite_room="", invite_role="")

@app.get("/consent/<token>")
def consent_link(token):
    item = INVITES.get(token)
    if not item or item["expires"] < time.time():
        INVITES.pop(token, None)
        abort(404, "Rozilik havolasi eskirgan yoki yaroqsiz.")
    return render_template("index.html", invite_room=item["room"], invite_role="device")

@app.post("/api/invitations")
def create_invitation():
    data = request.get_json(silent=True) or {}
    phone = str(data.get("phone", "")).strip()
    if not phone.startswith("+") or not phone[1:].isdigit() or not 8 <= len(phone[1:]) <= 15:
        return jsonify(error="Telefon raqamini xalqaro formatda kiriting, masalan +998901234567."), 400
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth = os.environ.get("TWILIO_AUTH_TOKEN")
    sender = os.environ.get("TWILIO_FROM_NUMBER")
    base = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
    if not all([sid, auth, sender, base]):
        return jsonify(error="SMS yuborish sozlanmagan. TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER va PUBLIC_BASE_URL kerak."), 503
    now = time.time()
    ip = request.remote_addr or "unknown"
    for key, limit in (("ip:" + ip, 5), ("phone:" + phone, 3)):
        recent = [t for t in SEND_LOG.get(key, []) if now - t < 3600]
        if len(recent) >= limit:
            return jsonify(error="SMS limiti tugadi. Keyinroq urinib ko‘ring."), 429
        SEND_LOG[key] = recent
    token = secrets.token_urlsafe(32)
    room = secrets.token_urlsafe(24)
    link = base + "/consent/" + token
    message = "Ulagich rozilik so‘rovi: " + link + " . Kamera/mikrofon faqat siz tasdiqlab, brauzer ruxsatini berganingizdan keyin ulanadi. Siz so‘ramagan bo‘lsangiz e’tiborsiz qoldiring. Havola 10 daqiqada eskiradi."
    body = urllib.parse.urlencode({"To": phone, "From": sender, "Body": message}).encode()
    endpoint = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    req = urllib.request.Request(endpoint, data=body, method="POST")
    req.add_header("Authorization", "Basic " + base64.b64encode(f"{sid}:{auth}".encode()).decode())
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status not in (200, 201):
                return jsonify(error="SMS provayderi xabarni qabul qilmadi."), 502
    except Exception:
        app.logger.exception("SMS yuborilmadi")
        return jsonify(error="SMS yuborilmadi. Provayder sozlamalarini tekshiring."), 502
    INVITES[token] = {"room": room, "expires": now + INVITE_TTL}
    for key in ("ip:" + ip, "phone:" + phone):
        SEND_LOG.setdefault(key, []).append(now)
    return jsonify(room=room, message="Rozilik havolasi SMS orqali yuborildi. Telefon egasining javobini kuting.")

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
