import datetime
import secrets

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from starlette.responses import HTMLResponse

from modules.notifications.services.users_email import UsersEmailService
from modules.notifications.settings import EmailSettings
from modules.users.dependencies import get_user_manager
from modules.users.fastapi_users_config import current_active_user
from modules.users.manager import UserManager
from modules.users.models import User
from modules.users.repositories import AccessTokenRepository
from modules.users.repositories.login_code import LoginCodeRepository
from modules.users.repositories.user import UserRepository
from modules.users.schemas.auth import LoginResponse, LoginWithEmailRequestSchema
from modules.users.schemas.user import UserCreate
from modules.users.services.auth_service import AuthMagicLinkService
from modules.users.settings import ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA, LOGIN_CODE_EXPIRES_IN_TIMEDELTA

router = APIRouter(prefix="/auth", tags=["Auth"])


# ==========================================================
# TODO MOVE LOGIC TO SERVICES
# ==========================================================


@router.post("/magic/login", response_model=LoginResponse)
async def login_with_magic_link(
    request: LoginWithEmailRequestSchema,
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    Переопределенный эндпоинт входа.
    Возвращает JSON с сообщением.

    Example:
    POST /magic/login
    {
        "email": "user@example.com"
    }

    Response:
    {
        "message": "Ссылка для входа отправлена на ваш email"
    }
    """
    try:
        auth_service = AuthMagicLinkService(
            UserRepository(user_manager.user_db.session),
            LoginCodeRepository(user_manager.user_db.session),
            UsersEmailService(EmailSettings())
        )
        await auth_service.login(request.email)
        # user_repository = UserRepository(user_manager.user_db.session)
        # user = await user_repository.get_by_email(request.email)
        #
        # if user is None:
        #     await user_repository.create(request.email)
        #
        # if not user.is_active:
        #     return LoginResponse(
        #         message="Если этот email зарегистрирован, вы получите ссылку для входа"
        #     )
        #
        # login_token = await LoginTokenRepository(user_manager.user_db.session).generate(
        #     user_id=user.id,
        #     expires_at=datetime.now(datetime.UTC) + LOGIN_CODE_EXPIRES_IN_TIMEDELTA,
        # )
        # try:
        #     await send_login_link(user.email, login_token)
        #     print(f"✓ Email входа отправлен на {user.email}")
        # except Exception as e:
        #     print(f"✗ Ошибка отправки email: {e}")
        #     raise HTTPException(
        #         status_code=500,
        #         detail="Ошибка отправки email. Попробуйте позже."
        #     )

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
        user_repository = UserRepository(user_manager.user_db.session)
        login_code = await LoginCodeRepository(user_manager.user_db.session).get(token)
        user = await user_repository.get(login_code.user_id)

        if not user.id or not user.email:
            raise ValueError("Code is incorrect")

        # Шаг 2: Получаем пользователя из БД
        # user = await user_manager.user_db.get_by_email(user.email)
        user = await user_repository.get_by_email(user.email)

        if user is None:
            raise ValueError("User not found")

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
        access_token = await AccessTokenRepository(user_manager.user_db.session).generate(
            user_id=user.id,
            expires_at=datetime.datetime.now(datetime.UTC) + ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA,
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
