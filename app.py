from flask import Flask, request, jsonify
import secrets, time

app = Flask(__name__)
tokens = {}
users = {}
TOKEN_EXPIRE = 10 * 60

def cleanup_tokens():
    now=time.time()
    for token in [t for t,d in tokens.items() if now-d["created"] > TOKEN_EXPIRE]:
        del tokens[token]

def generate_token():
    alphabet="ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "-".join("".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(2))

@app.route("/")
def home():
    return "<h1>Sign Token Server</h1><p>Server is running.</p>"

@app.route("/register", methods=["GET","POST"])
def register():
    cleanup_tokens()
    if request.method=="GET":
        return """<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">
        <style>body{background:#10131a;color:white;font-family:Arial;text-align:center;padding:45px 20px}
        input,button{padding:14px;margin:8px;border-radius:8px;border:0}button{background:#1769aa;color:white}</style>
        <h1>ZERO DAY TOOL</h1><h2>Sign Up</h2><form method="post">
        <input name="name" placeholder="Your name" required><br><button>Create Token</button></form>"""
    name=request.form.get("name","").strip()
    if not name: return "Name required",400
    key=name.casefold()
    if key in users: return "This name is already registered. Please use Sign In.",409
    token=generate_token()
    while token in tokens: token=generate_token()
    tokens[token]={"name":name,"created":time.time()}
    return f"""<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>body{{background:#10131a;color:white;font-family:Arial;text-align:center;padding:35px 15px}}
    .card{{max-width:600px;margin:auto;padding:35px;background:#1c202b;border-radius:22px}}
    .token{{margin:25px 0;padding:25px;background:#090c12;border-radius:16px;font-size:34px;letter-spacing:5px;font-weight:bold}}</style>
    <div class="card"><h1>Hello {name}</h1><p>Your one-time token:</p>
    <div class="token">{token}</div><p>Token expires in 10 minutes.</p><p>Enter it on the PC.</p></div>"""

@app.route("/verify", methods=["POST"])
def verify():
    cleanup_tokens()
    token=(request.get_json(silent=True) or {}).get("token","").strip().upper()
    if not token: return jsonify(success=False,message="Token required"),400
    data=tokens.get(token)
    if not data: return jsonify(success=False,message="Invalid or expired token"),401
    del tokens[token]
    name=data["name"]
    users[name.casefold()]={"name":name,"created":time.time()}
    return jsonify(success=True,name=name,message="Account created")

@app.route("/signin", methods=["POST"])
def signin():
    name=(request.get_json(silent=True) or {}).get("name","").strip()
    if not name: return jsonify(success=False,message="Name required"),400
    user=users.get(name.casefold())
    if not user: return jsonify(success=False,message="Account not found"),404
    return jsonify(success=True,name=user["name"],message="Signed in")

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)
