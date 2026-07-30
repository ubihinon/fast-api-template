"""Unit tests for AuthMagicLinkService.generate_code."""
from unittest.mock import patch

import pytest

from modules.users.services.auth_service import AuthMagicLinkService


@pytest.mark.unit
class TestGenerateCode:
    def test_code_is_six_digits(self):
        code = AuthMagicLinkService.generate_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_code_is_zero_padded(self):
        """A low random value (e.g. 7) must be zero-padded to 6 characters."""
        with patch("modules.users.services.auth_service.secrets.randbelow", return_value=7):
            code = AuthMagicLinkService.generate_code()
        assert code == "000007"
        assert len(code) == 6
