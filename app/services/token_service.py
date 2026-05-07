import base64
import hashlib
import hmac
import json
import time
from typing import Optional

from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRY_HOURS


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    return base64.urlsafe_b64decode(data + "=" * padding)


def _sign(message: str, secret: str) -> str:
    return _b64url_encode(
        hmac.HMAC(secret.encode(), message.encode(), hashlib.sha256).digest()
    )


def create_access_token(data: dict, expires_in_hours: Optional[int] = None) -> str:
    """Create a signed HS256 JWT."""
    header = _b64url_encode(json.dumps({"alg": JWT_ALGORITHM, "typ": "JWT"}).encode())
    payload = data.copy()
    payload["iat"] = int(time.time())
    payload["exp"] = int(time.time()) + (expires_in_hours or JWT_EXPIRY_HOURS) * 3600
    encoded_payload = _b64url_encode(json.dumps(payload).encode())
    signature = _sign(f"{header}.{encoded_payload}", JWT_SECRET_KEY)
    return f"{header}.{encoded_payload}.{signature}"


def decode_access_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT. Returns None if invalid or expired."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, payload, signature = parts
        expected_sig = _sign(f"{header}.{payload}", JWT_SECRET_KEY)
        if not hmac.compare_digest(expected_sig, signature):
            return None
        claims = json.loads(_b64url_decode(payload))
        if claims.get("exp", 0) < int(time.time()):
            return None
        return claims
    except Exception:
        return None
