# In main.py

import apps.load_model  # noqa
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware # <<< FIX: Import CORSMiddleware
from core import get_config
from core.exceptions.handlers import add_exception_handlers
from apps.auth.routes import auth_router
from apps.mails.routes import mail_router
from apps.images.routes import image_router
from apps.account.routes import account_router
from apps.blogs.routes import blog_router, blog_category_router
from apps.admin.routes import router as admin_router
from apps.errors.routes import router as error_router
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path


config = get_config()


app = FastAPI(title=config.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://eagis.ai",
        "http://eagis.ai:3000",
        "http://www.eagis.ai",
        "https://eagis.ai",
        "https://www.eagis.ai",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# existing middlewares
app.add_middleware(SessionMiddleware, secret_key=config.jwt_secrete, https_only=True)

# static files
app.mount("/static", StaticFiles(directory=config.static_path), name="static")
app.mount(
    "/uploads",
    StaticFiles(directory=Path.joinpath(config.root_path, config.local_storage_path)),
    name="uploads",
)


@app.get("/")
async def home():
    return "Welcome to Opt Flow backend apis"


# Routers
app.include_router(error_router)
app.include_router(auth_router)
app.include_router(mail_router)
app.include_router(image_router)
app.include_router(account_router)
app.include_router(blog_router)
app.include_router(blog_category_router)
app.include_router(admin_router)

# Exceptions
add_exception_handlers(app)