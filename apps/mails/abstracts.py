from abc import ABC, abstractmethod
from typing import Any, List


class MailAdapter(ABC):
    @abstractmethod
    async def send_email(
        self, subject: str, emails: List[str], template_name: str, data: dict[Any, Any]
    ) -> None:
        pass
