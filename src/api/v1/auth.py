import secrets
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from api.dependencies.auth.backend import auth_backend
from api.dependencies.auth.fastapi_users import current_active_user, fastapi_users
from models import AccessToken, User
from models.access_token import LoginToken
from schemas.user import LoginResponse, UserCreate, UserCreateMagicLink, UserRead
from fastapi import Depends, Query
from starlette.responses import HTMLResponse

from api.auth.user_manager import UserManager
from api.dependencies.auth.user_manager import get_user_manager




router = APIRouter(prefix="/auth", tags=["Auth"])

# /login and /logout
# router.include_router(
#     fastapi_users.get_auth_router(auth_backend),
# )


# /register
# router.include_router(
#     fastapi_users.get_register_router(UserRead, UserCreateMagicLink),
# )


# /request-verify-token and /verify
# router.include_router(fastapi_users.get_verify_router(UserRead))


@router.post("/magic/login", response_model=LoginResponse)
async def login_with_magic_link(
    # request: LoginWithEmailRequest,
    request: UserCreateMagicLink,
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    Переопределенный эндпоинт входа.
    Возвращает JSON с сообщением.

    Использование:
    POST /api/v1/auth/jwt/login
    {
        "email": "user@example.com"
    }

    Ответ:
    {
        "message": "Ссылка для входа отправлена на ваш email"
    }
    """
    try:
        # Проверяем, существует ли пользователь
        user = await user_manager.user_db.get_by_email(request.email)

        if user is None:
            user_create = UserCreate(
                email=request.email,
                password=secrets.token_urlsafe(32),
                is_active=True,
                is_verified=True
            )

            try:
                user = await user_manager.create(user_create)
                print(f"✓ Новый пользователь создан: {request.email}")
            except Exception as e:
                print(f"✗ Ошибка при создании пользователя: {e}")
                return LoginResponse(
                    message="Если этот email зарегистрирован, вы получите ссылку для входа"
                )

        # Проверяем, активен ли пользователь
        if not user.is_active:
            return LoginResponse(
                message="Если этот email зарегистрирован, вы получите ссылку для входа"
            )

        # Генерируем токен входа (действителен 15 минут)
        login_token = await _generate_login_token(user.id, user.email, user_manager.user_db)
        # access_token = await _generate_access_token(
        #     user.id,
        #     user.email,
        #     user_manager.user_db  # ← Передаем user_db
        # )
        # Отправляем email с ссылкой
        try:
            # await send_login_link(user.email, login_token)
            print(f"✓ Email входа отправлен на {user.email}")
        except Exception as e:
            print(f"✗ Ошибка отправки email: {e}")
            raise HTTPException(
                status_code=500,
                detail="Ошибка отправки email. Попробуйте позже."
            )

        return LoginResponse(
            message="Ссылка для входа отправлена на ваш email"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка сервера"
        )


@router.post("/magic/logout")
async def logout(
    user: User = Depends(current_active_user),
):
    return {"message": f"Пользователь {user.email} вышел из системы"}


@router.get("/magic/verify-login")
async def verify_login(
    token: str = Query(..., description="Токен входа из email"),
    user_manager: UserManager = Depends(get_user_manager),
):
    try:
        # Шаг 1: Декодируем токен входа
        payload = await _decode_login_token(token, user_db=user_manager.user_db)
        user_id = payload.get("user_id")
        email = payload.get("email")

        if not user_id or not email:
            raise ValueError("Неверный токен")

        # Шаг 2: Получаем пользователя из БД
        user = await user_manager.user_db.get_by_email(email)

        if user is None:
            raise ValueError("Пользователь не найден")

        # Шаг 3: Проверяем, активен ли пользователь
        if not user.is_active:
            return HTMLResponse(
                content="""
                <html>
                    <head>
                        <title>Аккаунт деактивирован</title>
                        <style>
                            body { 
                                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                                text-align: center; 
                                padding: 50px;
                                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                                color: white;
                                min-height: 100vh;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin: 0;
                            }
                            .container {
                                background: rgba(255, 255, 255, 0.1);
                                padding: 50px;
                                border-radius: 15px;
                                backdrop-filter: blur(10px);
                                max-width: 500px;
                            }
                            h1 { font-size: 36px; margin: 0 0 20px 0; }
                            .error-icon { font-size: 60px; margin-bottom: 20px; }
                            p { font-size: 16px; line-height: 1.6; margin: 10px 0; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="error-icon">🚫</div>
                            <h1>Аккаунт деактивирован</h1>
                            <p>Этот аккаунт был деактивирован.</p>
                        </div>
                    </body>
                </html>
                """,
                status_code=403
            )

        # Шаг 4: Генерируем access token и сохраняем в БД
        access_token = await _generate_access_token(
            user.id,
            user.email,
            user_manager.user_db
        )

        print(f"✓ Пользователь {user.email} вошел через Magic Link")
        print(f"✓ Access token: {access_token[:20]}...")

        # Шаг 5: Возвращаем HTML с токеном
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <title>Вход успешен</title>
                    <style>
                        body {{ 
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                            text-align: center; 
                            padding: 50px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            margin: 0;
                        }}
                        .container {{
                            background: rgba(255, 255, 255, 0.1);
                            padding: 50px;
                            border-radius: 15px;
                            backdrop-filter: blur(10px);
                            max-width: 500px;
                        }}
                        h1 {{
                            font-size: 36px;
                            margin: 0 0 20px 0;
                        }}
                        .success-icon {{
                            font-size: 60px;
                            margin-bottom: 20px;
                        }}
                        p {{
                            font-size: 16px;
                            line-height: 1.6;
                            margin: 10px 0;
                        }}
                        .token {{
                            background: rgba(0, 0, 0, 0.2);
                            padding: 15px;
                            border-radius: 5px;
                            margin: 20px 0;
                            word-break: break-all;
                            font-family: monospace;
                            font-size: 12px;
                            max-height: 100px;
                            overflow-y: auto;
                        }}
                        a {{ 
                            display: inline-block;
                            margin-top: 30px;
                            padding: 12px 30px;
                            background: #4caf50;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            font-weight: bold;
                            transition: background 0.3s;
                        }}
                        a:hover {{ 
                            background: #45a049;
                        }}
                    </style>
                    <script>
                        // Сохраняем токен в localStorage
                        localStorage.setItem('access_token', '{access_token}');

                        // Редиректим на главную страницу через 2 секунды
                        setTimeout(() => {{
                            window.location.href = 'http://localhost:3000/dashboard';
                        }}, 2000 );
                    </script>
                </head>
                <body>
                    <div class="container">
                        <div class="success-icon">✅</div>
                        <h1>Вход успешен!</h1>
                        <p>Вы вошли в систему как {user.email}</p>
                        <p style="font-size: 14px; color: #ddd;">Перенаправление на главную страницу...</p>
                        <div class="token">
                            Токен: {access_token}
                        </div>
                        <a href="http://localhost:3000/dashboard">Перейти на сайт</a>
                    </div>
                </body>
            </html>
            """,
            status_code=200
        )

    # Обработка ошибки: токен истек
    except jwt.ExpiredSignatureError:
        print(f"✗ Ошибка: токен истек")
        return HTMLResponse(
            content="""
            <html>
                <head>
                    <title>Ссылка истекла</title>
                    <style>
                        body { 
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                            text-align: center; 
                            padding: 50px;
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            color: white;
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            margin: 0;
                        }
                        .container {
                            background: rgba(255, 255, 255, 0.1);
                            padding: 50px;
                            border-radius: 15px;
                            backdrop-filter: blur(10px);
                            max-width: 500px;
                        }
                        h1 { font-size: 36px; margin: 0 0 20px 0; }
                        .error-icon { font-size: 60px; margin-bottom: 20px; }
                        p { font-size: 16px; line-height: 1.6; margin: 10px 0; }
                        a { 
                            display: inline-block;
                            margin-top: 30px;
                            padding: 12px 30px;
                            background: #ff9800;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            font-weight: bold;
                        }
                        a:hover { background: #e68900; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="error-icon">⏰</div>
                        <h1>Ссылка истекла</h1>
                        <p>Ссылка для входа действительна только 15 минут.</p>
                        <a href="http://localhost:3000/login">Запросить новую ссылку</a>
                    </div>
                </body>
            </html>
            """,
            status_code=400
        )

    # Обработка ошибки: неверный токен
    except jwt.InvalidTokenError:
        print(f"✗ Ошибка: неверный токен")
        return HTMLResponse(
            content="""
            <html>
                <head>
                    <title>Ошибка входа</title>
                    <style>
                        body { 
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                            text-align: center; 
                            padding: 50px;
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            color: white;
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            margin: 0;
                        }
                        .container {
                            background: rgba(255, 255, 255, 0.1);
                            padding: 50px;
                            border-radius: 15px;
                            backdrop-filter: blur(10px);
                            max-width: 500px;
                        }
                        h1 { font-size: 36px; margin: 0 0 20px 0; }
                        .error-icon { font-size: 60px; margin-bottom: 20px; }
                        p { font-size: 16px; line-height: 1.6; margin: 10px 0; }
                        a { 
                            display: inline-block;
                            margin-top: 30px;
                            padding: 12px 30px;
                            background: #ff9800;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            font-weight: bold;
                        }
                        a:hover { background: #e68900; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="error-icon">❌</div>
                        <h1>Ошибка входа</h1>
                        <p>Неверная ссылка.</p>
                        <a href="http://localhost:3000/login">Попробовать снова</a>
                    </div>
                </body>
            </html>
            """,
            status_code=400
        )

    # Обработка ошибки: пользователь не найден или другие ошибки
    except Exception as e:
        print(f"✗ Ошибка при входе: {e}")
        return HTMLResponse(
            content="""
            <html>
                <head>
                    <title>Ошибка входа</title>
                    <style>
                        body { 
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                            text-align: center; 
                            padding: 50px;
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            color: white;
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            margin: 0;
                        }
                        .container {
                            background: rgba(255, 255, 255, 0.1);
                            padding: 50px;
                            border-radius: 15px;
                            backdrop-filter: blur(10px);
                            max-width: 500px;
                        }
                        h1 { font-size: 36px; margin: 0 0 20px 0; }
                        .error-icon { font-size: 60px; margin-bottom: 20px; }
                        p { font-size: 16px; line-height: 1.6; margin: 10px 0; }
                        a { 
                            display: inline-block;
                            margin-top: 30px;
                            padding: 12px 30px;
                            background: #ff9800;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            font-weight: bold;
                        }
                        a:hover { background: #e68900; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="error-icon">❌</div>
                        <h1>Ошибка входа</h1>
                        <p>Произошла ошибка сервера. Попробуйте позже.</p>
                        <a href="http://localhost:3000/login">Попробовать снова</a>
                    </div>
                </body>
            </html>
            """,
            status_code=500
        )

async def _generate_access_token(
    user_id: str,
    email: str,
    user_db,
    expires_in_hours: int = 24
) -> str:
    # 1. Генерируем случайный токен (64 символа)
    token = secrets.token_urlsafe(48)

    # 2. Вычисляем время истечения
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

    # 3. Получаем сессию БД
    session = user_db.session

    # 4. Создаем запись в БД
    session.add(AccessToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at,
        is_active=True
    ))

    # 5. Сохраняем в БД
    await session.commit()

    # 6. Возвращаем токен
    return token


async def _generate_login_token(user_id: str, email: str, user_db, expires_in_minutes: int = 15) -> str:
    """Генерирует обычный токен и сохраняет в БД."""
    token = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)

    session = user_db.session
    session.add(LoginToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at,
        is_active=True,
    ))
    await session.commit()
    return token


async def _decode_login_token(token: str, user_db) -> dict:
    session = user_db.session

    query = select(LoginToken).where(
        LoginToken.token == token,
        LoginToken.is_active == True,
        LoginToken.expires_at > datetime.utcnow()
    )
    result = await session.execute(query)
    login_token_record = result.scalar_one_or_none()

    if not login_token_record:
        raise ValueError("Токен неверный или истек")

    user = await user_db.get(login_token_record.user_id)
    return {"user_id": str(user.id), "email": user.email}
