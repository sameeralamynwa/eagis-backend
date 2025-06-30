from fastapi import APIRouter, Request
from core.jinja import get_template_rederer
from jinja2 import FileSystemLoader
from .config import get_config

config = get_config()

render = get_template_rederer(
    FileSystemLoader(str(config.template_path)),
)


mail_router = APIRouter(tags=["mails"], prefix="/test-mails")


@mail_router.get("/verify-email")
async def get_verify_email(request: Request):
    context = {
        "data": {"name": "john doe", "otp": "578945"},
    }
    return render(request, "mails/verify_email.html", context=context)


@mail_router.get("/forgot-password")
async def get_forgot_password_email(request: Request):
    context = {
        "data": {"name": "john doe", "otp": "578945"},
    }
    return render(request, "mails/forgot_password.html", context=context)
