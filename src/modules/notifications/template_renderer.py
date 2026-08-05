from gettext import NullTranslations
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from core.i18n import DEFAULT_LANGUAGE, _translations, current_language

TEMPLATES_DIR = Path(__file__).parent / "templates"

_envs: dict[str, Environment] = {}


def _get_env(lang: str) -> Environment:
    if lang not in _envs:
        translation: NullTranslations = (
            _translations.get(lang) or _translations.get(DEFAULT_LANGUAGE) or NullTranslations()
        )
        env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            extensions=["jinja2.ext.i18n"],
            autoescape=True,
            auto_reload=False,
        )
        env.install_gettext_translations(translation, newstyle=True)  # type: ignore[attr-defined]
        _envs[lang] = env
    return _envs[lang]


def render_email_template(template_name: str, context: dict) -> str:
    lang = current_language.get()
    return _get_env(lang).get_template(template_name).render(**context)
