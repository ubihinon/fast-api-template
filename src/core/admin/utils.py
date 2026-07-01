import bcrypt

from core.settings import settings


def hash_password(password: str) -> str:
    if len(password) < settings.ADMIN_PASSWORD_MIN_LENGTH:
        raise ValueError(f"Password must be at least {settings.ADMIN_PASSWORD_MIN_LENGTH} symbols")

    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt(rounds=12)

    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(password_bytes, hashed_bytes)
