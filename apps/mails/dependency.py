import asyncio
from typing import Annotated, Any, List
from fastapi import Depends
from .adapters import FastMailAdapter, DevMailAdapter
from .config import Config, MailAdapters, get_config


class MailService:
    def __init__(
        self,
        config: Annotated[Config, Depends(get_config)],
    ):
        if config.mail_adapter == MailAdapters.FASTMAIL:
            self.adapter = FastMailAdapter(config=config)
        elif config.mail_adapter == MailAdapters.DEV:
            # <<< CHANGE: Pass the config object here as well
            self.adapter = DevMailAdapter(config=config)
        else:
            raise ValueError(f"Unsupported mail adapter: {config.mail_adapter}")

    async def send_mail(
        self,
        subject: str,
        emails: List[str],
        template_name: str,
        data: dict[Any, Any],
    ) -> None:
        await self.adapter.send_email(
            subject=subject, data=data, emails=emails, template_name=template_name
        )


MailServiceDependency = Annotated[MailService, Depends()]


# test only
if __name__ == "__main__":
    config = get_config()
    mail_service = MailService(config=config)
    mail_data = {
        "config": config,
        "data": {"name": "john doe", "otp": "578945"},
    }

    asyncio.run(
        mail_service.send_mail(
            subject="Test-1",
            data=mail_data,
            emails=["john@gmail.com"],
            template_name="mails/verify_email.html",
        )
    )