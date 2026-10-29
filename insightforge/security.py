import base64, hashlib, hmac, json, secrets, time

def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return base64.b64encode(salt + digest).decode()

def verify_password(password, encoded):
    raw = base64.b64decode(encoded); salt, expected = raw[:16], raw[16:]
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return hmac.compare_digest(actual, expected)

def issue_session(user, secret, ttl=3600):
    payload = {"sub": user["id"], "email": user["email"], "role": user["role"],
               "exp": int(time.time()) + ttl, "nonce": secrets.token_hex(8)}
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    sig = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return body + "." + sig

def read_session(token, secret):
    try:
        body, sig = token.rsplit(".", 1)
        expected = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected): return None
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        return payload if payload.get("exp", 0) >= time.time() else None
    except (ValueError, TypeError, json.JSONDecodeError): return None
