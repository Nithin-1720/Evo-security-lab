import jwt

from fastapi import APIRouter, Form, HTTPException

from app.auth.passwords import verify_password
from app.db import get_connection


router = APIRouter(
    prefix="/api/auth",
    tags=["API Authentication"],
)


#
# INTENTIONALLY HARDCODED AND WEAK.
#
JWT_SECRET = "evo-weak-jwt-secret"


@router.post("/token")
def create_token(
    username: str = Form(...),
    password: str = Form(...),
):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,),
    ).fetchone()

    connection.close()

    if not user or not verify_password(
        password,
        user["password_hash"],
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    #
    # INTENTIONAL WEAKNESS:
    #
    # No expiration.
    # No issuer.
    # No audience.
    # Weak hardcoded signing key.
    #

    token = jwt.encode(
        {
            "sub": user["username"],
            "user_id": user["id"],
            "role": user["role"],
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/insecure-me")
def insecure_me(token: str):

    #
    # INTENTIONAL CRITICAL AUTHENTICATION FLAW:
    #
    # JWT signature verification is disabled.
    #

    try:

        payload = jwt.decode(
            token,
            options={
                "verify_signature": False
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "authenticated": True,
        "identity": payload,
    }