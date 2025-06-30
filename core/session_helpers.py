from fastapi import Request
from typing import Literal


def flash(request: Request, message: str, type: Literal["error", "warn", "success"]):
    request.session.setdefault("_flashes", []).append(
        {"message": message, "type": type}
    )


def get_flashed_messages(request: Request):
    messages = request.session.pop("_flashes", [])
    return messages
