"""Unit tests for AuthMagicLinkService.generate_code."""
import pytest

from modules.users.services.auth_service import AuthMagicLinkService


@pytest.mark.unit
class TestGenerateCode:
    def test_code_is_six_digits(self):
        code = AuthMagicLinkService.generate_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_code_is_zero_padded(self):
        """Codes with low random values must still be 6 characters wide."""
        for _ in range(50):
            assert len(AuthMagicLinkService.generate_code()) == 6
