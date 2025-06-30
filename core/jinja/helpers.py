from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, Environment, FileSystemLoader
from . import global_env
from core import get_config


config = get_config()
jinja2templates = Jinja2Templates(env=global_env)


def add_template_loaders(env: Environment, new_loader: FileSystemLoader):
    current_loader = env.loader

    if isinstance(env.loader, ChoiceLoader):
        # Append the new loader to existing list
        current_loader.loaders.append(new_loader)  # type: ignore
    else:
        # Replace with a ChoiceLoader containing both
        env.loader = ChoiceLoader([current_loader, new_loader])  # type: ignore


def get_template_rederer(new_loader: FileSystemLoader | None = None):
    if new_loader:
        add_template_loaders(global_env, new_loader)

    return jinja2templates.TemplateResponse
