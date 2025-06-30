from fastapi import APIRouter, Request
from jinja2 import FileSystemLoader
from core.jinja import get_template_rederer
from .config import get_config


router = APIRouter(prefix="/errors")

config = get_config()
render = get_template_rederer(
    FileSystemLoader(str(config.template_path)),
)


@router.get("/not-found", name="errors.not_found")
def not_found(request: Request):
    return render(request, "errors/not_found.html.j2")


@router.get("/access-denied", name="errors.access_denied")
def access_denied(request: Request):
    return render(request, "errors/access_denied.html.j2")


@router.get("/http-error", name="errors.http")
def http_error(request: Request):
    return render(request, "errors/http_error.html.j2")
