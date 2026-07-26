"""Unit tests for AuthMagicLinkService.generate_code."""
from unittest.mock import MagicMock

import pytest

from modules.users.services.auth_service import AuthMagicLinkService


@pytest.mark.unit
class TestGenerateCode:
    def _make(self) -> AuthMagicLinkService:
        service = MagicMock(spec=AuthMagicLinkService)
        service.generate_code = AuthMagicLinkService.generate_code.__get__(service)
        return service

    def test_code_is_six_digits(self):
        code = self._make().generate_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_code_is_zero_padded(self):
        """Codes with low random values must still be 6 characters wide."""
        service = self._make()
        for _ in range(50):
            assert len(service.generate_code()) == 6
