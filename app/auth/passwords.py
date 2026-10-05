import hashlib


def hash_password(password: str) -> str:
    """
    INTENTIONALLY INSECURE LAB IMPLEMENTATION.

    SHA-1 is deliberately used so SAST tooling has a weak
    cryptographic/password-storage pattern to identify.

    Never use this implementation in a real application.
    """

    return hashlib.sha1(password.encode("utf-8")).hexdigest()


def verify_password(password: str, expected_hash: str) -> bool:
    return hash_password(password) == expected_hash