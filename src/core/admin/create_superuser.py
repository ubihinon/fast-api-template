import sys

from core.admin.models import UserAdmin
from core.admin.utils import hash_password
from core.database import async_session, sync_session


def add_test_users():
    """Добавление тестовых пользователей"""
    with sync_session() as session:
        try:




            # Проверяем, есть ли уже пользователи
            existing_users = session.query(UserAdmin).count()
            if existing_users > 0:
                print("⚠️  Пользователи уже существуют в БД. Пропускаем добавление.")
                return

            print("👥 Добавление тестовых пользователей...")

            # Суперпользователь
            admin_user = UserAdmin(
                username="admin",
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                full_name="Administrator",
                is_active=True,
                is_superuser=True,
            )
            session.add(admin_user)
            print("  ✓ Добавлен суперпользователь: admin / admin123")

            # Обычный пользователь
            regular_user = UserAdmin(
                username="user",
                email="user@example.com",
                password_hash=hash_password("user123"),
                full_name="John Doe",
                is_active=True,
                is_superuser=False,
            )
            session.add(regular_user)
            print("  ✓ Добавлен обычный пользователь: user / user123")

            # Еще один пользователь
            another_user = UserAdmin(
                username="editor",
                email="editor@example.com",
                password_hash=hash_password("editor123"),
                full_name="Jane Editor",
                is_active=True,
                is_superuser=False,
            )
            session.add(another_user)
            print("  ✓ Добавлен редактор: editor / editor123")

            session.commit()
            print("✅ Пользователи добавлены успешно!")

        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка при добавлении пользователей: {e}")
            sys.exit(1)

add_test_users()
