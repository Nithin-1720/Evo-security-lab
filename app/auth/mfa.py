import base64
import io
import secrets

import pyotp
import qrcode


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(username: str, secret: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name="Evo Vulnerable AI Lab",
    )


def generate_qr_data_uri(uri: str) -> str:
    qr = qrcode.make(uri)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")

    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return f"data:image/png;base64,{encoded}"


def verify_totp(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(
        code,
        valid_window=1,
    )


def generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"