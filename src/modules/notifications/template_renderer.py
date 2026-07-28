from gettext import NullTranslations
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from core.i18n import DEFAULT_LANGUAGE, _translations, current_language

TEMPLATES_DIR = Path(__file__).parent / "templates"


def render_email_template(template_name: str, context: dict) -> str:
    lang = current_language.get()
    translation: NullTranslations = _translations.get(lang) or _translations.get(DEFAULT_LANGUAGE) or NullTranslations()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        extensions=["jinja2.ext.i18n"],
        autoescape=True,
    )
    env.install_gettext_translations(translation, newstyle=True)  # type: ignore[attr-defined]

    return env.get_template(template_name).render(**context)
