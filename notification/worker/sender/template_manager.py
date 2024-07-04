import os

from .exceptions import TemplateNotExist
from jinja2 import Environment, FileSystemLoader
from core.settings import EVENT_TO_TEMPLATE


class TemplateRenderManager:
    """Класс для управления шаблонами."""

    def __init__(self) -> None:
        self.env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))

    def render_template(self, message_dict: dict) -> str:
        """Генерация шаблона для отправки письма."""
        event = message_dict.get("event")

        if event not in EVENT_TO_TEMPLATE:
            raise TemplateNotExist

        template = self.env.get_template(EVENT_TO_TEMPLATE[event])
        return template.render(**message_dict.get("context"))
