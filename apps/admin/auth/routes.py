from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from jinja2 import FileSystemLoader
from core.jinja.helpers import get_template_rederer
from core.session_helpers import flash
from .dtos import LoginForm
from apps.auth.dependency import AuthDependency
from core import ConfigDepedency
from core.exceptions.common import UnAuthorizedException
from ..config import get_config

router = APIRouter(tags=["Admin"])

config = get_config()

render = get_template_rederer(
    FileSystemLoader(str(config.template_path)),
)


@router.api_route(
    "/login", methods=["GET", "POST"], name="admin.login", operation_id="admin_login"
)
async def login(
    request: Request,
    auth: AuthDependency,
    app_config: ConfigDepedency,
):
    form_data = await request.form()
    form = LoginForm(form_data, meta={"csrf_context": request.session})

    if request.method == "POST" and form.validate():
        try:
            access_token = await auth.login(form.username.data, form.password.data)
            response = RedirectResponse(request.url_for("admin.dashboard"), 303)
            response.set_cookie(
                key="auth_token",
                value=access_token,
                max_age=app_config.access_token_expire_minutes * 60,
                httponly=True,
                secure=app_config.app_in_prod,
            )

            return response
        except UnAuthorizedException as e:
            flash(request, e.detail, "error")
            raise e

    return render(request, "admin/auth/login.html.j2", {"form": form})


@router.post("/logout", name="admin.logout")
async def logout(
    request: Request,
    app_config: ConfigDepedency,
):
    response = RedirectResponse(request.url_for("admin.dashboard"), 303)
    response.delete_cookie(
        key="auth_token",
        httponly=True,
        secure=app_config.app_in_prod,
    )

    return response
