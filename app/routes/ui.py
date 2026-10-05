from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db import get_connection


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def require_login(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=302)

    return None


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    redirect = require_login(request)

    if redirect:
        return redirect

    connection = get_connection()

    customer_count = connection.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    user_count = connection.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    audit_count = connection.execute(
        "SELECT COUNT(*) FROM audit_events"
    ).fetchone()[0]

    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "customer_count": customer_count,
            "user_count": user_count,
            "audit_count": audit_count,
        },
    )


@router.get("/customers-ui", response_class=HTMLResponse)
def customers_ui(request: Request):

    redirect = require_login(request)

    if redirect:
        return redirect

    connection = get_connection()

    customers = connection.execute(
        "SELECT * FROM customers ORDER BY id"
    ).fetchall()

    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="customers.html",
        context={
            "customers": customers,
        },
    )


@router.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):

    redirect = require_login(request)

    if redirect:
        return redirect

    #
    # INTENTIONAL BROKEN ACCESS CONTROL
    #
    # We deliberately DO NOT check:
    #
    # request.session["role"] == "admin"
    #
    # Any authenticated user can therefore access this page.
    #

    connection = get_connection()

    users = connection.execute(
        """
        SELECT id,
               username,
               display_name,
               role,
               totp_enabled,
               otp_enabled
        FROM users
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "users": users,
        },
    )


@router.get("/lab", response_class=HTMLResponse)
def lab_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="lab.html",
        context={},
    )

@router.get(
    "/lab/mailbox",
    response_class=HTMLResponse,
)
def lab_mailbox(request: Request):

    connection = get_connection()

    messages = connection.execute(
        """
        SELECT
            id,
            recipient,
            subject,
            body,
            otp_code,
            created_at
        FROM lab_mailbox
        ORDER BY id DESC
        LIMIT 25
        """
    ).fetchall()

    connection.close()

    #
    # INTENTIONAL LAB VULNERABILITY:
    #
    # Mailbox is accessible without authentication
    # and exposes OTP values.
    #

    return templates.TemplateResponse(
        request=request,
        name="mailbox.html",
        context={
            "messages": messages,
        },
    )


@router.get(
    "/api-lab",
    response_class=HTMLResponse,
)
def api_lab(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="api_lab.html",
        context={},
    )

@router.get(
    "/ai-chat",
    response_class=HTMLResponse,
)
def ai_chat_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="ai_chat.html",
        context={},
    )