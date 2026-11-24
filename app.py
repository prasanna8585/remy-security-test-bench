"""Small internal user-management API + a couple of admin tools.
Run with: python app.py (listens on :5000)"""
import re

from flask import Flask, request, jsonify, render_template

import auth
import db
from utils.mailer import send_email
from utils.fetch import fetch_preview
from utils.profile_import import import_profile_bundle
from utils.logs import export_user_log

app = Flask(__name__)
db.init_db()


def login_required(fn):
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-Session-Token")
        user_id = auth.current_user_id(token)
        if user_id is None:
            return jsonify({"error": "unauthorized"}), 401
        request.user_id = user_id
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return wrapper


def _sanitize_username(username):
    # strip anything that isn't alnum/underscore/dash to keep log filenames sane
    return re.sub(r"[^a-zA-Z0-9_\-]", "", username)


@app.route("/api/register", methods=["POST"])
def register():
    body = request.get_json()
    pw_hash = auth.hash_password(body["password"])
    user_id = db.create_user(body["email"], pw_hash, body.get("display_name", ""))
    send_email(body["email"], "Welcome!", "Thanks for signing up.")
    return jsonify({"user_id": user_id})


@app.route("/api/login", methods=["POST"])
def login_route():
    body = request.get_json()
    token = auth.login(body["email"], body["password"])
    if token is None:
        return jsonify({"error": "invalid credentials"}), 401
    return jsonify({"token": token})


@app.route("/api/users/<int:user_id>/profile", methods=["GET"])
@login_required
def get_profile(user_id):
    # Any logged-in user can view any profile page by id - this mirrors a lot of
    # "public profile" features (think LinkedIn-style profile URLs).
    row = db.get_user_by_id(user_id)
    if row is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(
        {
            "id": row["id"],
            "email": row["email"],
            "display_name": row["display_name"],
        }
    )


@app.route("/api/users/<int:user_id>/profile/html", methods=["GET"])
@login_required
def get_profile_html(user_id):
    row = db.get_user_by_id(user_id)
    if row is None:
        return "not found", 404
    bio = request.args.get("bio_preview", row["display_name"] or "")
    return render_template(
        "profile.html",
        display_name_html=row["display_name"],
        bio=bio,
        member_since="2024",
    )


@app.route("/api/admin/search", methods=["GET"])
@login_required
def admin_search():
    name_query = request.args.get("q", "")
    rows = db.search_users_by_name(name_query)
    return jsonify([dict(r) for r in rows])


@app.route("/api/link-preview", methods=["GET"])
@login_required
def link_preview():
    url = request.args.get("url")
    preview = fetch_preview(url)
    return jsonify(preview)


@app.route("/api/password-reset/start", methods=["POST"])
def password_reset_start():
    body = request.get_json()
    row = db.get_connection().execute(
        "SELECT id, email FROM users WHERE email = ?", (body["email"],)
    ).fetchone()
    if row is None:
        return jsonify({"ok": True})  # don't leak whether the email exists
    token = auth.start_password_reset(row["id"])
    send_email(row["email"], "Reset your password", f"Your reset code: {token}")
    return jsonify({"ok": True})


@app.route("/api/password-reset/resend", methods=["POST"])
def password_reset_resend():
    """User clicked 'didn't get it? resend' on the reset page."""
    body = request.get_json()
    row = db.get_connection().execute(
        "SELECT id, email FROM users WHERE email = ?", (body["email"],)
    ).fetchone()
    if row is None:
        return jsonify({"ok": True})
    token = auth.resend_password_reset(row["id"])
    send_email(row["email"], "Reset your password", f"Your new reset code: {token}")
    return jsonify({"ok": True})


@app.route("/api/password-reset/complete", methods=["POST"])
def password_reset_complete():
    body = request.get_json()
    ok = auth.complete_password_reset(
        body["user_id"], body["token"], auth.hash_password(body["new_password"])
    )
    if not ok:
        return jsonify({"error": "invalid or expired token"}), 400
    return jsonify({"ok": True})


@app.route("/api/profile/import", methods=["POST"])
@login_required
def profile_import():
    bundle = request.get_data()
    data = import_profile_bundle(request.user_id, bundle)
    return jsonify({"imported_keys": list(data.keys()) if isinstance(data, dict) else None})


@app.route("/api/admin/export-log", methods=["POST"])
@login_required
def admin_export_log():
    body = request.get_json()
    username = _sanitize_username(body["username"])
    output_format = body.get("format", "zip")
    path = export_user_log(username, output_format)
    return jsonify({"archive": path})


if __name__ == "__main__":
    app.run(debug=True)
