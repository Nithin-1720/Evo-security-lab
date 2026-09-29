from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(
    prefix="/api/render",
    tags=["Rendering"],
)


@router.get("/", response_class=HTMLResponse)
def render_message(message: str):

    # INTENTIONALLY VULNERABLE.
    page = f"""
    <html>

        <body>

            <h1>Customer Message</h1>

            <div>
                {message}
            </div>

        </body>

    </html>
    """

    return HTMLResponse(page)