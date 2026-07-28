from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.i18n import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, current_language


class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: object) -> Response:
        lang = self._detect_language(request)
        token = current_language.set(lang)
        try:
            return await call_next(request)  # type: ignore[operator]
        finally:
            current_language.reset(token)

    def _detect_language(self, request: Request) -> str:
        if lang := request.query_params.get("lang"):
            if lang in SUPPORTED_LANGUAGES:
                return lang

        accept_lang = request.headers.get("Accept-Language", "")
        for part in accept_lang.split(","):
            code = part.strip().split(";")[0].strip()[:2]
            if code in SUPPORTED_LANGUAGES:
                return code

        return DEFAULT_LANGUAGE
