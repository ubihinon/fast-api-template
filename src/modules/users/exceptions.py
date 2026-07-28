from core.i18n import _


class AccessTokenNotFound(Exception):
    pass


class AuthErrorException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UserNotFoundException(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(_("User with email %(email)s not found") % {"email": email})


class LoginCodeInvalidException(Exception):
    def __init__(self):
        super().__init__(_("Code is invalid or expired"))


class LoginCodeNotFoundException(Exception):
    def __init__(self, code_id: int):
        self.code_id = code_id
        super().__init__(_("Code with id '%(code_id)s' not found") % {"code_id": code_id})


class LoginMaxNumberAttemptsException(Exception):
    def __init__(self, message: str = ""):
        self.message = message or _("Maximum number of attempts exceeded")
        super().__init__(self.message)
