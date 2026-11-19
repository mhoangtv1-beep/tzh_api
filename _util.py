import base64
import json
import os
import random
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.backends import default_backend

INVISIBLE_CHARS = ["\u200b", "\u200c", "\u200d", "\ufeff"]

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def gen_nonce(length: int = 32) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choice(alphabet) for _ in range(length))

def generate_p256_key():
    return ec.generate_private_key(ec.SECP256R1(), default_backend())

def pub_coord_bytes(key) -> bytes:
    pts = key.public_key().public_numbers()
    return b"\x04" + pts.x.to_bytes(32, "big") + pts.y.to_bytes(32, "big")

def build_dpop_token(key, method: str, url: str) -> str:
    pts = key.public_key().public_numbers()
    jwk = {
        "crv": "P-256",
        "kty": "EC",
        "x": b64url(pts.x.to_bytes(32, "big")),
        "y": b64url(pts.y.to_bytes(32, "big"))
    }
    hdr = json.dumps({"alg": "ES256", "typ": "dpop+jwt", "jwk": jwk}, separators=(",", ":")).encode("utf-8")
    claim = json.dumps({
        "jti": b64url(os.urandom(32)),
        "htm": method,
        "htu": url,
        "iat": int(time.time())
    }, separators=(",", ":")).encode("utf-8")
    payload = f"{b64url(hdr)}.{b64url(claim)}"
    sig = key.sign(payload.encode("utf-8"), ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(sig)
    return f"{payload}.{b64url(r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))}"

def mask_text(content: str) -> str:
    salt = "".join(random.choices(INVISIBLE_CHARS, k=random.randint(2, 6)))
    return content + salt

def encode_varint(value):
    out = bytearray()
    while value > 0x7f:
        out.append((value & 0x7f) | 0x80)
        value >>= 7
    out.append(value & 0x7f)
    return bytes(out)

def decode_varint(buf, offset=0):
    val, shift = 0, 0
    pos = offset
    while pos < len(buf):
        b = buf[pos]
        val |= (b & 0x7f) << shift
        pos += 1
        if not (b & 0x80):
            break
        shift += 7
    return val, pos

def pb_field(tag, wire_type, data):
    header = encode_varint((tag << 3) | wire_type)
    if wire_type == 0:
        return header + encode_varint(data)
    elif wire_type == 2:
        return header + encode_varint(len(data)) + data
    raise ValueError("Unsupported wire_type")

def build_im_message_payload(cid, text, sender_uid):
    msg_body = json.dumps({"text": text}, ensure_ascii=False).encode('utf-8')
    client_msg_id = str(int(time.time() * 1000) * 1000 + random.randint(100, 999))
    body = bytearray()
    body.extend(pb_field(1, 2, cid.encode('utf-8')))
    body.extend(pb_field(2, 0, 1))
    body.extend(pb_field(3, 0, 7))
    body.extend(pb_field(4, 2, msg_body))
    body.extend(pb_field(5, 2, client_msg_id.encode('utf-8')))
    body.extend(pb_field(6, 0, int(sender_uid) if str(sender_uid).isdigit() else 0))
    body.extend(pb_field(7, 0, int(time.time() * 1000)))
    return bytes(body)

def extract_cookie_val(cookie_str: str, key: str) -> str:
    for chunk in cookie_str.split(";"):
        parts = chunk.strip().split("=", 1)
        if len(parts) == 2 and parts[0].strip() == key:
            return parts[1].strip()
    return ""
