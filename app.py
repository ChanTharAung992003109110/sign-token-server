from flask import Flask, request, jsonify
import secrets
import time

app = Flask(__name__)

# Temporary in-memory token storage
tokens = {}
TOKEN_EXPIRE = 10 * 60  # 10 minutes

def cleanup_tokens():
    now = time.time()
    expired = [
        token
        for token, data in tokens.items()
        if now - data["created"] > TOKEN_EXPIRE
    ]
    for token in expired:
        del tokens[token]

def generate_token():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "-".join(
        "".join(secrets.choice(alphabet) for _ in range(4))
        for _ in range(2)
    )

@app.route("/")
def home():
    return """
    <h1>Sign Token Server</h1>
    <p>Server is running.</p>
    """

@app.route("/register", methods=["GET", "POST"])
def register():
    cleanup_tokens()

    if request.method == "GET":
        return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Get Token</title>
<style>
body {
    margin:0;
    background:#10131a;
    color:white;
    font-family:Arial;
}
.box {
    max-width:380px;
    margin:80px auto;
    padding:30px;
    background:#1b202b;
    border-radius:20px;
}
input {
    width:100%;
    box-sizing:border-box;
    padding:14px;
    margin:10px 0;
    border:0;
    border-radius:10px;
    font-size:16px;
}
button {
    width:100%;
    padding:14px;
    border:0;
    border-radius:10px;
    background:#3478f6;
    color:white;
    font-size:16px;
    font-weight:bold;
}
</style>
</head>
<body>
<div class="box">
<h2>Get Token</h2>
<form method="POST">
<input name="name" placeholder="Enter your name" maxlength="60" required>
<button type="submit">Generate Token</button>
</form>
</div>
</body>
</html>
"""

    name = request.form.get("name", "").strip()
    if not name:
        return "Name required", 400

    token = generate_token()
    while token in tokens:
        token = generate_token()

    tokens[token] = {
        "name": name,
        "created": time.time()
    }

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Your Token</title>
<style>
body {{
    margin:0;
    background:#10131a;
    color:white;
    font-family:Arial;
}}
.box {{
    max-width:380px;
    margin:80px auto;
    padding:30px;
    background:#1b202b;
    border-radius:20px;
    text-align:center;
}}
.token {{
    margin:25px 0;
    padding:20px;
    background:#0d1117;
    border-radius:12px;
    font-size:30px;
    font-weight:bold;
    letter-spacing:4px;
}}
</style>
</head>
<body>
<div class="box">
<h2>Hello {name}</h2>
<p>Your one-time token:</p>
<div class="token">
{token}
</div>
<p>Token expires in 10 minutes.</p>
<p>Enter this token on the PC.</p>
</div>
</body>
</html>
"""

@app.route("/verify", methods=["POST"])
def verify():
    cleanup_tokens()
    data = request.get_json(silent=True) or {}
    token = data.get("token", "").strip().upper()

    if not token:
        return jsonify({
            "success": False,
            "message": "Token required"
        }), 400

    token_data = tokens.get(token)
    if not token_data:
        return jsonify({
            "success": False,
            "message": "Invalid or expired token"
        }), 401

    # ONE-TIME TOKEN: consume it so it can't be used again
    del tokens[token]

    return jsonify({
        "success": True,
        "name": token_data["name"],
        "message": "Token accepted"
    })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
