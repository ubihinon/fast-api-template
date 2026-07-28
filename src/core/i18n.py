from contextvars import ContextVar
from gettext import NullTranslations
from pathlib import Path

from babel.support import Translations

LOCALES_DIR = Path(__file__).parent.parent / "locales"
SUPPORTED_LANGUAGES = ["en", "ru"]
DEFAULT_LANGUAGE = "en"

current_language: ContextVar[str] = ContextVar("current_language", default=DEFAULT_LANGUAGE)

_translations: dict[str, NullTranslations] = {}


def load_translations() -> None:
    for lang in SUPPORTED_LANGUAGES:
        _translations[lang] = Translations.load(str(LOCALES_DIR), [lang])


def _(text: str) -> str:
    lang = current_language.get()
    translation = _translations.get(lang, _translations.get(DEFAULT_LANGUAGE))
    if translation is None:
        return text
    return translation.gettext(text)
