# In core/exceptions/handlers.py

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# <<< CHANGE: The specific ForbiddenException and NotFoundException imports are no longer needed
from core.exceptions.common import UnAuthorizedException
from core.jinja.helpers import get_template_rederer

render = get_template_rederer()


def add_exception_handlers(app: FastAPI):
    """Adds common exception hanlders and returns BaseResponse."""

    def wants_html(request: Request) -> bool:
        accept = request.headers.get("accept", "")
        return "text/html" in accept.lower()

    @app.exception_handler(UnAuthorizedException)
    async def unauthorized_exception_hanlder(
        request: Request, exc: UnAuthorizedException
    ):
        if wants_html(request):
            return RedirectResponse(request.url_for("admin.login"), 303)

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc.detail)},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if wants_html(request):
            if exc.status_code == 404:
                return render(request, "errors/not_found.html.j2", status_code=404)
            if exc.status_code == 401:
                return RedirectResponse(request.url_for("admin.login"), 303)
            if exc.status_code == 403:
                return render(request, "errors/access_denied.html.j2", status_code=403)
            
            return render(
                request, "errors/http_error.html.j2", {"error": str(exc.detail)}, status_code=exc.status_code
            )

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc.detail)},
        )

    @app.exception_handler(ResponseValidationError)
    async def response_validation_exception_handler(
        request: Request, exc: ResponseValidationError
    ):
        # This handler is specific and should remain.
        if wants_html(request):
            return render(request, "errors/http_error.html.j2", status_code=422)
        return JSONResponse(
            status_code=422,
            content={"detail": "Server Response Validation Error - " + str(exc)},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        if wants_html(request):
            return render(request, "errors/http_error.html.j2", status_code=500)
        return JSONResponse(
            status_code=500,
            content={"detail": "Server Error - " + str(exc)},
        )