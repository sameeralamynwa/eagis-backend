from fastapi import APIRouter, Request, Depends
from jinja2 import FileSystemLoader
from apps.auth.dependency import is_authenticated
from core.jinja.helpers import get_template_rederer
from .users.routes import router as user_router
from .auth.routes import router as auth_router
from .roles.routes import router as roles_router
from .images.routes import router as images_router
from .blog_categories.routes import router as blog_category_router
from .blogs.routes import router as blogs_router
from apps.auth.dependency import AuthDependency
from .config import get_config

router = APIRouter(prefix="/admin", tags=["Admin"])
router.include_router(auth_router)
router.include_router(user_router, prefix="/users")
router.include_router(roles_router, prefix="/roles")
router.include_router(images_router, prefix="/images")
router.include_router(blog_category_router, prefix="/blog-categories")
router.include_router(blogs_router, prefix="/blogs")

config = get_config()
render = get_template_rederer(
    FileSystemLoader(str(config.template_path)),
)


@router.get("/", name="admin.dashboard", dependencies=[Depends(is_authenticated)])
async def dashboard(request: Request, auth: AuthDependency):
    user = await auth.get_user_or_raise()
    return render(request, "admin/dashboard.html.j2", {"user": user})
