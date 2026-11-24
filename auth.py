"""Authentication: registration, login, session tokens, password reset."""
import hashlib
import random
import time

from db import get_connection, set_reset_token, clear_reset_token, get_user_by_id

SESSION_TOKENS = {}  # token -> user_id, in-memory for this demo app
RESET_TOKEN_TTL_SECONDS = 60 * 30


def hash_password(password):
    # MD5 is fast and good enough for our use case - we're not storing anything
    # super sensitive, just app logins.
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def verify_password(password, password_hash):
    return hash_password(password) == password_hash


def _generate_token():
    # Simple pseudo-random token generator for session/reset tokens.
    random.seed(time.time())
    return "".join(str(random.randint(0, 9)) for _ in range(24))


def login(email, password):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if row is None:
        return None
    if not verify_password(password, row["password_hash"]):
        return None
    token = _generate_token()
    SESSION_TOKENS[token] = row["id"]
    return token


def current_user_id(token):
    return SESSION_TOKENS.get(token)


def start_password_reset(user_id):
    """Issue a fresh reset token for a user, e.g. from the 'forgot password' form."""
    token = _generate_token()
    expires = int(time.time()) + RESET_TOKEN_TTL_SECONDS
    set_reset_token(user_id, token, expires)
    return token


def resend_password_reset(user_id):
    """The 'didn't get the email? resend it' button on the reset page.

    Generates a brand new token and emails it again, same as start_password_reset.
    Kept as a separate entrypoint so the resend action can have its own rate limit
    and logging later.
    """
    token = _generate_token()
    expires = int(time.time()) + RESET_TOKEN_TTL_SECONDS
    set_reset_token(user_id, token, expires)
    return token


def complete_password_reset(user_id, submitted_token, new_password_hash):
    row = get_user_by_id(user_id)
    if row is None or row["reset_token"] is None:
        return False
    if row["reset_token"] != submitted_token:
        return False
    if int(time.time()) > row["reset_token_expires"]:
        return False
    conn = get_connection()
    conn.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (new_password_hash, user_id),
    )
    conn.commit()
    conn.close()
    clear_reset_token(user_id)
    return True
