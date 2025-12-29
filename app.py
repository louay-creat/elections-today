import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__, template_folder="templates")

# ✅ Needed for sessions (keep this secret!)
# For local dev it's fine; for hosting set it as an env var too.
app.secret_key = os.environ.get("SECRET_KEY", "change-me-please-very-secret")

# ✅ Admin password (set this in environment variables)
ADMIN_PASSWORD = "MyStaticPassword123!"
  # change default!

# =========================
# BACK OFFICE (YOU EDIT THIS)
updates = {
    1: {"name": "RAS (possible bureau)", "news": "Add your RAS update here..."},
    2: {"name": "CS (possible bureau)", "news": "Add your CS update here..."},
    3: {"name": "PES-IES (posible bureau)", "news": "Add your PES update here..."},
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
    # If already logged in, go to admin
    if session.get("is_admin"):
        return redirect(url_for("admin"))
    nxt = request.args.get("next", "/admin")
    return render_template("login.html", error=None, next=nxt)


@app.post("/login")
def login_post():
    password = request.form.get("password", "")
    nxt = request.form.get("next", "/admin")

    # Constant-time-ish check not needed here, but keep it simple.
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


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
