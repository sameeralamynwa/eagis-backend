from typing import Annotated, Any, List
from fastapi import Depends
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from .config import Config, get_config
from .abstracts import MailAdapter


class FastMailAdapter(MailAdapter):
    """Fast mail adapter to send real emails"""

    def __init__(
        self,
        config: Annotated[Config, Depends(get_config)],
    ) -> None:
        self.conf = ConnectionConfig(
            MAIL_USERNAME=config.smtp_username,
            MAIL_PASSWORD=config.smtp_password.get_secret_value(), # Use .get_secret_value() for SecretStr
            MAIL_FROM="test@email.com",
            MAIL_PORT=config.smtp_port,
            MAIL_SERVER=config.smtp_host,
            MAIL_FROM_NAME="Admin",
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            TEMPLATE_FOLDER=config.template_path,
        )

    async def send_email(
        self, subject: str, emails: List[str], template_name: str, data: dict[Any, Any]
    ) -> None:
        message = MessageSchema(
            subject=subject,
            recipients=emails,
            template_body=data,
            subtype=MessageType.html,
        )

        fm = FastMail(self.conf)
        await fm.send_message(message, template_name=template_name)


class DevMailAdapter(MailAdapter):
    """
    Dev mail adapter to send emails in dev environment only.
    It Will Print the email data to console.
    """

    # <<< CHANGE: Add this __init__ method for consistency
    def __init__(self, config: Config) -> None:
        # We don't need to use the config, but accepting it makes this
        # class perfectly interchangeable with FastMailAdapter.
        self.config = config

    async def send_email(
        self, subject: str, emails: List[str], template_name: str, data: dict[Any, Any]
    ) -> None:
        print("=" * 20)
        print("--- DEV EMAIL ---")
        print(f"Subject: {subject}")
        print(f"To: {emails}")
        print(f"Template: {template_name}")
        print("Data:")
        print(data)
        print("--- END DEV EMAIL ---")
        print("=" * 20)