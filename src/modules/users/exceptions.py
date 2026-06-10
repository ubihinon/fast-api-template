class AuthErrorException(Exception):
    pass


class UserNotFoundException(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {email} not found")


# class LoginCodeNotFoundException(Exception):
#     def __init__(self, code: str):
#         self.code = code
#         super().__init__(f"Code '{self.code}' not found")
#

class LoginCodeInvalidException(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(f"Code '{self.code}' is invalid or not found")


class LoginCodeExpiredException(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(f"Code '{self.code}' is expired")


class LoginCodeInactiveException(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(f"Code '{self.code}' already used")


class LoginMaxNumberAttemptsException(Exception):
    def __init__(self, message: str = "Maximum number of attempts exceeded"):
        self.message = message
        super().__init__(message)
