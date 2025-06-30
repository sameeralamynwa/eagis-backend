from jinja2 import ChoiceLoader, Environment, FileSystemLoader
from core import get_config
from .globals import globals as global_vars


config = get_config()
GLOBAL_TEMPLATES = config.root_path / "templates"

global_env = Environment()
global_env.loader = ChoiceLoader(
    [
        FileSystemLoader(str(GLOBAL_TEMPLATES)),
    ]
)

global_env.globals.update(global_vars)
