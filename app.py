import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder="templates")

# Needed for sessions (change this!)
app.secret_key = "CHANGE_THIS_SECRET_KEY_123456789"

# 🔒 STATIC ADMIN PASSWORD (change this!)
ADMIN_PASSWORD = "MyStrongPassword123!"

# =========================
# BACK OFFICE (YOU EDIT THIS)
updates = {
    1: {"name": "RAS (possible bureau)", "news": "Add your RAS update here..."},
    2: {"name": "CS (possible bureau)", "news": "Add your CS update here..."},
    3: {"name": "PES (iesposible bureau)", "news": "Add your PES update here..."},
    4: {"name": "IAS (posible bureau)", "news": "Add your IAS update here..."},
    5: {"name": "EMBS (posible bureau)", "news": "Add your EMBS update here..."},
    6: {"name": "WIE (posible bureau)", "news": "Add your WIE update here..."},
    7: {"name": "CAS (posible bureau)", "news": "Add your CAS update here..."},
}
# =========================


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper


@app.get("/")
def home():
    selected = request.args.get("n", type=int)
    item = updates.get(selected) if selected in updates else None
    return render_template("index.html", updates=updates, item=item, selected=selected)


@app.get("/login")
def login():
    if session.get("is_admin"):
        return redirect(url_for("admin"))
    nxt = request.args.get("next", "/admin")
    return render_template("login.html", error=None, next=nxt)


@app.post("/login")
def login_post():
    password = request.form.get("password", "")
    nxt = request.form.get("next", "/admin")

    if password == ADMIN_PASSWORD:
        session["is_admin"] = True
        return redirect(nxt if nxt.startswith("/") else "/admin")

    return render_template("login.html", error="Wrong password.", next=nxt)


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.get("/admin")
@login_required
def admin():
    return render_template("admin.html", updates=updates)


@app.post("/update")
@login_required
def update():
    n = int(request.form["n"])
    news = request.form["news"]
    if n in updates:
        updates[n]["news"] = news
    return redirect(url_for("admin"))


if __name__ == "__main__":
    # ✅ IMPORTANT for Replit/Render: use PORT + 0.0.0.0
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
