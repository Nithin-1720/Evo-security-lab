from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.routes import customers
from app.routes import files
from app.routes import render
from app.routes import ai
from app.routes import auth
from app.routes import ui
from app.routes import vulnerable
from app.routes import api_auth
from app.routes import admin_api

app = FastAPI(
    title="Evo Vulnerable AI Lab",
    description=(
        "Deliberately vulnerable application for testing "
        "Snyk SCA, SAST, API & Web, Container, IaC, Secrets and Evo."
    ),
    version="1.0.0",
)


#
# INTENTIONALLY INSECURE LAB CONFIGURATION
#
# Hard-coded secret.
# HTTPS-only cookies are disabled.
#

app.add_middleware(
    SessionMiddleware,
    secret_key="EVO-LAB-INSECURE-SESSION-SECRET-DO-NOT-USE",
    https_only=False,
    same_site="lax",
)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


app.include_router(auth.router)
app.include_router(ui.router)

# Existing vulnerable APIs
app.include_router(customers.router)
app.include_router(files.router)
app.include_router(render.router)
app.include_router(ai.router)
app.include_router(vulnerable.router)
app.include_router(api_auth.router)
app.include_router(admin_api.router)


@app.get("/")
def root(request: Request):

    if request.session.get("user_id"):
        return RedirectResponse(
            "/dashboard",
            status_code=302,
        )

    return RedirectResponse(
        "/login",
        status_code=302,
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "application": "Evo Vulnerable AI Lab",
    }