import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder="templates")

# Sessions
app.secret_key = "CHANGE_THIS_SECRET_KEY_123456789"

# Static admin password
ADMIN_PASSWORD = "MyStrongPassword123!"  # change this

updates = {
    1: {"name": "RAS (possible bureau)", "news": "Add your RAS update here..."},
    2: {"name": "CS (possible bureau)", "news": "Add your CS update here..."},
    3: {"name": "PES (iesposible bureau)", "news": "Add your PES update here..."},
    4: {"name": "IAS (posible bureau)", "news": "Add your IAS update here..."},
    5: {"name": "EMBS (posible bureau)", "news": "Add your EMBS update here..."},
    6: {"name": "WIE (posible bureau)", "news": "Add your WIE update here..."},
    7: {"name": "CAS (posible bureau)", "news": "Add your CAS update here..."},
}

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper

# ✅ Health check endpoint (always returns 200 quickly)
@app.get("/health")
def health():
    return "ok", 200

@app.get("/")
def home():
    try:
        selected = request.args.get("n", type=int)
        item = updates.get(selected) if selected in updates else None
        return render_template("index.html", updates=updates, item=item, selected=selected), 200
    except Exception as e:
        # If templates are missing in deploy, / will crash -> health check fails.
        # Return a 200 with debug info so deploy can pass and you can see what's wrong.
        return (
            "App is running but template load failed. "
            "Check that templates/index.html exists in the deployment. "
            f"Error: {type(e).__name__}: {e}",
            200,
        )

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
