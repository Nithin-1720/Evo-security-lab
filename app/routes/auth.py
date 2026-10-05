from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.mfa import (
    generate_otp,
    verify_totp,
)
from app.auth.passwords import verify_password
from app.db import get_connection
from app.auth.mfa import (
    generate_otp,
    generate_qr_data_uri,
    generate_totp_secret,
    get_totp_uri,
    verify_totp,
)

router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


def complete_login(request: Request, user):

    request.session.clear()

    request.session["user_id"] = user["id"]
    request.session["username"] = user["username"]
    request.session["display_name"] = user["display_name"]
    request.session["role"] = user["role"]
    request.session["mfa_verified"] = True


def get_pending_user(request: Request):

    user_id = request.session.get(
        "pending_user_id"
    )

    if not user_id:
        return None

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    connection.close()

    return user


@router.get(
    "/login",
    response_class=HTMLResponse
)
def login_page(request: Request):

    if request.session.get("user_id"):
        return RedirectResponse(
            "/dashboard",
            status_code=302,
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None
        },
    )


@router.post(
    "/login",
    response_class=HTMLResponse
)
def login(
    request: Request,
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

    if not user or not verify_password(
        password,
        user["password_hash"],
    ):

        connection.execute(
            """
            INSERT INTO audit_events
            (
                username,
                event_type,
                details,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                "LOGIN_FAILURE",
                "Invalid username or password",
                datetime.utcnow().isoformat(),
            ),
        )

        connection.commit()
        connection.close()

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error":
                    "Invalid username or password"
            },
            status_code=401,
        )

    #
    # First factor succeeded.
    #
    # Do NOT authenticate the user yet.
    #

    request.session.clear()

    request.session["pending_user_id"] = (
        user["id"]
    )

    request.session["pending_username"] = (
        user["username"]
    )


    #
    # TOTP takes priority.
    #

    if user["totp_enabled"]:

        connection.close()

        return RedirectResponse(
            "/mfa/totp",
            status_code=303,
        )


    #
    # Email-style OTP.
    #

    if user["otp_enabled"]:

        otp_code = generate_otp()

        connection.execute(
            """
            INSERT INTO lab_mailbox
            (
                user_id,
                recipient,
                subject,
                body,
                otp_code,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                f"{user['username']}@lab.local",
                "Your Evo Lab login code",
                (
                    "Your Evo Vulnerable AI Lab "
                    f"authentication code is {otp_code}"
                ),
                otp_code,
                datetime.utcnow().isoformat(),
            ),
        )

        connection.commit()
        connection.close()

        return RedirectResponse(
            "/mfa/otp",
            status_code=303,
        )


    #
    # No MFA configured.
    #

    complete_login(
        request,
        user,
    )

    connection.execute(
        """
        INSERT INTO audit_events
        (
            username,
            event_type,
            details,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            username,
            "LOGIN_SUCCESS",
            "Password-only authentication",
            datetime.utcnow().isoformat(),
        ),
    )

    connection.commit()
    connection.close()

    return RedirectResponse(
        "/dashboard",
        status_code=303,
    )


@router.get(
    "/mfa/totp",
    response_class=HTMLResponse,
)
def totp_page(request: Request):

    user = get_pending_user(request)

    if not user:
        return RedirectResponse(
            "/login",
            status_code=302,
        )

    return templates.TemplateResponse(
        request=request,
        name="mfa_totp.html",
        context={
            "error": None
        },
    )


@router.post(
    "/mfa/totp",
    response_class=HTMLResponse,
)
def totp_verify(
    request: Request,
    code: str = Form(...),
):

    user = get_pending_user(request)

    if not user:
        return RedirectResponse(
            "/login",
            status_code=302,
        )

    if not user["totp_secret"]:

        return RedirectResponse(
            "/login",
            status_code=302,
        )

    if not verify_totp(
        user["totp_secret"],
        code,
    ):

        return templates.TemplateResponse(
            request=request,
            name="mfa_totp.html",
            context={
                "error":
                    "Invalid authenticator code"
            },
            status_code=401,
        )

    complete_login(
        request,
        user,
    )

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO audit_events
        (
            username,
            event_type,
            details,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user["username"],
            "MFA_TOTP_SUCCESS",
            "TOTP authentication successful",
            datetime.utcnow().isoformat(),
        ),
    )

    connection.commit()
    connection.close()

    return RedirectResponse(
        "/dashboard",
        status_code=303,
    )


@router.get(
    "/mfa/otp",
    response_class=HTMLResponse,
)
def otp_page(request: Request):

    user = get_pending_user(request)

    if not user:
        return RedirectResponse(
            "/login",
            status_code=302,
        )

    return templates.TemplateResponse(
        request=request,
        name="mfa_otp.html",
        context={
            "error": None
        },
    )


@router.post(
    "/mfa/otp",
    response_class=HTMLResponse,
)
def otp_verify(
    request: Request,
    code: str = Form(...),
):

    user = get_pending_user(request)

    if not user:
        return RedirectResponse(
            "/login",
            status_code=302,
        )

    connection = get_connection()

    message = connection.execute(
        """
        SELECT *
        FROM lab_mailbox
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user["id"],),
    ).fetchone()


    #
    # INTENTIONALLY WEAK MFA IMPLEMENTATION
    #
    # No expiration.
    # No retry limit.
    # OTP stored in plaintext.
    #
    # Useful for SAST / API & Web testing.
    #

    if not message or (
        message["otp_code"] != code
    ):

        connection.close()

        return templates.TemplateResponse(
            request=request,
            name="mfa_otp.html",
            context={
                "error": "Invalid OTP code"
            },
            status_code=401,
        )

    complete_login(
        request,
        user,
    )

    connection.execute(
        """
        INSERT INTO audit_events
        (
            username,
            event_type,
            details,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user["username"],
            "MFA_OTP_SUCCESS",
            "OTP authentication successful",
            datetime.utcnow().isoformat(),
        ),
    )

    connection.commit()
    connection.close()

    return RedirectResponse(
        "/dashboard",
        status_code=303,
    )



@router.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        "/login",
        status_code=302,
    )







@router.get(
    "/mfa/setup/totp",
    response_class=HTMLResponse,
)
def setup_totp(request: Request):

    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(
            "/login",
            status_code=302,
        )

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    secret = (
        user["totp_secret"]
        or generate_totp_secret()
    )

    if not user["totp_secret"]:

        connection.execute(
            """
            UPDATE users
            SET totp_secret = ?
            WHERE id = ?
            """,
            (
                secret,
                user_id,
            ),
        )

        connection.commit()

    connection.close()

    uri = get_totp_uri(
        user["username"],
        secret,
    )

    qr_data = generate_qr_data_uri(uri)

    return templates.TemplateResponse(
        request=request,
        name="totp_setup.html",
        context={
            "secret": secret,
            "qr_data": qr_data,
            "error": None,
        },
    )


@router.post(
    "/mfa/setup/totp",
    response_class=HTMLResponse,
)
def enable_totp(
    request: Request,
    code: str = Form(...),
):

    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(
            "/login",
            status_code=302,
        )

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    if not verify_totp(
        user["totp_secret"],
        code,
    ):

        uri = get_totp_uri(
            user["username"],
            user["totp_secret"],
        )

        qr_data = generate_qr_data_uri(uri)

        connection.close()

        return templates.TemplateResponse(
            request=request,
            name="totp_setup.html",
            context={
                "secret":
                    user["totp_secret"],
                "qr_data":
                    qr_data,
                "error":
                    "Invalid authenticator code",
            },
            status_code=400,
        )

    connection.execute(
        """
        UPDATE users
        SET totp_enabled = 1
        WHERE id = ?
        """,
        (user_id,),
    )

    connection.commit()
    connection.close()

    return RedirectResponse(
        "/dashboard",
        status_code=303,
    )