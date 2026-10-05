from fastapi import APIRouter

from app.db import get_connection


router = APIRouter(
    prefix="/api/admin",
    tags=["Vulnerable Admin API"],
)


@router.get("/users")
def get_all_users():

    #
    # INTENTIONAL BROKEN ACCESS CONTROL:
    #
    # No authentication or admin-role check.
    #

    connection = get_connection()

    users = connection.execute(
        """
        SELECT
            id,
            username,
            display_name,
            password_hash,
            role,
            totp_secret,
            totp_enabled,
            otp_enabled
        FROM users
        """
    ).fetchall()

    connection.close()

    return [
        dict(user)
        for user in users
    ]


@router.get("/audit")
def get_audit_events():

    #
    # INTENTIONAL BROKEN ACCESS CONTROL.
    #

    connection = get_connection()

    events = connection.execute(
        """
        SELECT *
        FROM audit_events
        ORDER BY id DESC
        LIMIT 100
        """
    ).fetchall()

    connection.close()

    return [
        dict(event)
        for event in events
    ]


@router.get("/customer-notes")
def get_all_customer_notes():

    #
    # INTENTIONAL DATA EXPOSURE.
    #

    connection = get_connection()

    notes = connection.execute(
        """
        SELECT *
        FROM customer_notes
        """
    ).fetchall()

    connection.close()

    return [
        dict(note)
        for note in notes
    ]