"""
INTENTIONALLY VULNERABLE LAB FILE.

All credentials are synthetic and have no access to any
external or production system.
"""


DATABASE_PASSWORD = "SuperUnsafeLabDatabasePassword_2026!"

JWT_SECRET = (
    "6a84e14f34b828f1c87509ea27dfe662"
    "4e18aa55c9a01f65f850b7899bf67e42"
)

INTERNAL_API_KEY = (
    "3ce1ed63c8c89cb5d546315508155dc8"
    "95d06b874bc6ee392218bb20574a0181"
)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "LabAdmin123!"


def get_database_connection_string():
    return (
        "postgresql://evo_lab_admin:"
        "SuperUnsafeLabDatabasePassword_2026!"
        "@database.internal:5432/evo_lab"
    )