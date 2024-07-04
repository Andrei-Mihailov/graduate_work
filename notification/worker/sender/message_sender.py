import uuid
from typing import Tuple

import sib_api_v3_sdk
from core.settings import settings, Status
from sib_api_v3_sdk.rest import ApiException
from db.store import Store
from .template_manager import TemplateRenderManager


class SendMessageManager:
    """Класс управляет рассылками по электронной почте."""

    def __init__(self) -> None:
        self.configuration = sib_api_v3_sdk.Configuration()
        self.configuration.api_key["api-key"] = settings.api_key_email
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(self.configuration)
        )
        self.store = Store()
        self.template_render = TemplateRenderManager()

    def send(self, message: dict) -> bool:
        subject = "Уведомление от сервиса notification service."
        to_send, from_send = self._prepare_data_for_message(message)
        notification_id = str(uuid.uuid4())
        status = None
        context = self.template_render.render_template(message)
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to_send, html_content=context, sender=from_send, subject=subject
        )
        try:
            self.api_instance.send_transac_email(send_smtp_email)
            status = Status.SUCCESS.value
        except ApiException:
            status = Status.FAIL.value
            return False
        self.store.save_notification(
            {"id": notification_id, "status": status, "context": context}
        )
        return True

    @staticmethod
    def _prepare_data_for_message(
        message: dict,
    ) -> Tuple[list[dict[str, str]], dict[str, str]]:
        email: str = message.get("email")
        name = email.split("@")[0]
        to_send = [{"email": email, "name": name}]
        from_send = {"name": settings.sender_name, "email": settings.sender_email}
        return to_send, from_send
