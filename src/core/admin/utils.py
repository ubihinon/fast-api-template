import hashlib
import secrets

from core.settings import settings


def hash_password(password: str) -> str:
    """
    Хеширование пароля с солью
    
    ВНИМАНИЕ: В production используйте bcrypt или argon2!
    Это простой пример для демонстрации.
    """
    if len(password) < settings.ADMIN_PASSWORD_MIN_LENGTH:
        raise ValueError(f"Пароль должен быть не менее {settings.ADMIN_PASSWORD_MIN_LENGTH} символов")
    
    # Генерируем соль
    salt = secrets.token_hex(16)
    
    # Хешируем пароль с солью
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000  # количество итераций
    )
    
    # Возвращаем соль + хеш в формате "salt$hash"
    return f"{salt}${password_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """
    Проверка пароля против хеша
    """
    try:
        salt, stored_hash = password_hash.split("$")
        
        # Хешируем введенный пароль с той же солью
        password_check = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        )
        
        # Сравниваем хеши
        return password_check.hex() == stored_hash
    except (ValueError, AttributeError):
        return False
