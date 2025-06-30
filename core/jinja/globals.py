from datetime import datetime
from core import get_config
from core.session_helpers import get_flashed_messages

config = get_config()


def css_version():
    if config.app_in_dev:
        return datetime.now().timestamp()
    return config.css_version


globals = {
    "css_version": css_version,
    "app_name": config.app_name,
    "app_url": config.app_url,
    "app_in_dev": config.app_in_dev,
    "app_in_prod": config.app_in_prod,
    "get_flashed_messages": get_flashed_messages,
}
