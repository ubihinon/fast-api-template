class AccessTokenNotFound(Exception):
    pass


class AuthErrorException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UserNotFoundException(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {email} not found")


class LoginCodeInvalidException(Exception):
    def __init__(self):
        super().__init__("Code is invalid or expired")


class LoginCodeNotFoundException(Exception):
    def __init__(self, code_id: int):
        self.code_id = code_id
        super().__init__(f"Code with id '{code_id}' not found")


class LoginMaxNumberAttemptsException(Exception):
    def __init__(self, message: str = "Maximum number of attempts exceeded"):
        self.message = message
        super().__init__(message)
