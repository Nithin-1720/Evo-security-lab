from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routes.customers import router as customers_router
from app.routes.render import router as render_router
from app.routes.files import router as files_router

app = FastAPI(
    title="Evo Vulnerable AI Lab",
    description="Intentionally vulnerable AI application for security testing",
    version="1.0.0",
)

app.include_router(customers_router)
app.include_router(render_router)
app.include_router(files_router)



@app.get("/")
def home():
    return {
        "application": "Evo Vulnerable AI Lab",
        "status": "running",
        "purpose": "security testing only",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/welcome", response_class=HTMLResponse)
def welcome():
    return """
    <html>
        <head>
            <title>Evo Vulnerable AI Lab</title>
        </head>

        <body>

            <h1>Evo Vulnerable AI Lab</h1>

            <p>
                Deliberately vulnerable application
                for Snyk security testing.
            </p>

        </body>
    </html>
    """