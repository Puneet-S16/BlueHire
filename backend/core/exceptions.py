class DuplicateEmailError(Exception):
    def __init__(self, message="Email already registered"):
        self.message = message
        super().__init__(self.message)


class InvalidCredentialsError(Exception):
    def __init__(self, message="Invalid credentials"):
        self.message = message
        super().__init__(self.message)


class InactiveUserError(Exception):
    def __init__(self, message="User account is inactive"):
        self.message = message
        super().__init__(self.message)


class RefreshTokenNotFoundError(Exception):
    def __init__(self, message="Refresh token not found or revoked"):
        self.message = message
        super().__init__(self.message)
