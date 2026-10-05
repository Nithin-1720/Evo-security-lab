import os
import subprocess

import requests
import yaml

from fastapi import APIRouter, Body, Request
from fastapi.responses import RedirectResponse

from app.db import get_connection
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/api/vuln",
    tags=["Deliberately Vulnerable Lab APIs"],
)


class ProfileUpdate(BaseModel):
    email: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None

    # INTENTIONALLY VULNERABLE:
    # A normal user should never be able to set their own role.
    role: Optional[str] = None

#
# LAB-API-001
# IDOR / BOLA
#
@router.get("/customers/{customer_id}/note")
def customer_note(customer_id: int):

    connection = get_connection()

    note = connection.execute(
        """
        SELECT
            customer_id,
            note,
            sensitivity
        FROM customer_notes
        WHERE customer_id = ?
        """,
        (customer_id,),
    ).fetchone()

    connection.close()

    #
    # INTENTIONAL VULNERABILITY:
    #
    # There is no authentication and no authorization.
    # Anyone can request any customer's private note.
    #

    if not note:
        return {
            "error": "Customer note not found"
        }

    return dict(note)


#
# LAB-API-002
# SSRF
#
@router.get("/fetch")
def fetch_url(url: str):

    #
    # INTENTIONAL VULNERABILITY:
    #
    # User controls the complete URL.
    #
    # No:
    #   scheme validation
    #   hostname allowlist
    #   private-IP blocking
    #   redirect validation
    #

    response = requests.get(
        url,
        timeout=5,
    )

    return {
        "url": url,
        "status_code": response.status_code,
        "body": response.text[:2000],
    }


#
# LAB-API-003
# Command injection
#
@router.get("/diagnostics/ping")
def diagnostic_ping(host: str):

    if os.name == "nt":
        command = f"ping -n 1 {host}"
    else:
        command = f"ping -c 1 {host}"

    #
    # INTENTIONAL VULNERABILITY:
    #
    # User-controlled value is concatenated into a shell command.
    #

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=10,
    )

    return {
        "command": command,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "return_code": result.returncode,
    }


#
# LAB-API-004
# Unsafe YAML deserialization
#
@router.post("/yaml/import")
def import_yaml(
    document: str = Body(
        ...,
        media_type="text/plain",
    )
):

    #
    # INTENTIONAL VULNERABILITY:
    #
    # yaml.Loader is intentionally unsafe for untrusted input.
    #

    parsed = yaml.load(
        document,
        Loader=yaml.Loader,
    )

    return {
        "status": "imported",
        "parsed": parsed,
    }


#
# LAB-API-005
# Open redirect
#
@router.get("/redirect")
def redirect(next: str):

    #
    # INTENTIONAL VULNERABILITY:
    #
    # No validation that the destination belongs to this application.
    #

    return RedirectResponse(
        url=next,
        status_code=302,
    )


#
# LAB-API-006
# Sensitive information exposure
#
@router.get("/internal/config")
def internal_config():

    #
    # All values below are synthetic lab values.
    #

    return {
        "environment": "production-demo",
        "database": "customers.db",
        "database_username": "evo_lab_admin",
        "database_password": "LabDatabasePassword123!",
        "internal_api_key": "EVO-INTERNAL-LAB-KEY-123456",
        "jwt_signing_key": "evo-weak-jwt-secret",
        "debug": True,
    }


#
# LAB-API-007
# Mass assignment
#
@router.put("/users/{user_id}/profile")
def update_profile(
    user_id: int,
    data: ProfileUpdate,
):

    #
    # INTENTIONAL MASS ASSIGNMENT VULNERABILITY
    #
    # The API accepts fields directly from the user.
    # "role" should never be modifiable through a normal
    # profile-update endpoint.
    #

    allowed_database_fields = {
        "email",
        "department",
        "phone",
        "role",
    }

    updates = []
    values = []

    for key, value in data.model_dump(
    exclude_none=True
    ).items():

        if key in allowed_database_fields:

            updates.append(
                f"{key} = ?"
            )

            values.append(value)

    if not updates:

        return {
            "status": "nothing updated"
        }

    values.append(user_id)

    sql = (
        "UPDATE user_profiles SET "
        + ", ".join(updates)
        + " WHERE user_id = ?"
    )

    connection = get_connection()

    connection.execute(
        sql,
        values,
    )

    connection.commit()

    profile = connection.execute(
        """
        SELECT *
        FROM user_profiles
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()

    connection.close()

    return {
        "status": "updated",
        "profile": (
            dict(profile)
            if profile
            else None
        ),
    }


#
# LAB-API-008
# Information disclosure
#
@router.get("/debug/request")
def debug_request(request: Request):

    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "cookies": request.cookies,
        "client": (
            request.client.host
            if request.client
            else None
        ),
    }