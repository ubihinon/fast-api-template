# Модульный монолит: разделение зависимостей между modules/users и modules/notifications

## Проблема

Модуль `users` напрямую импортировал `UsersEmailService` из модуля `notifications` в 4 местах:

- `modules/users/manager.py`
- `modules/users/services/auth_service.py`
- `modules/users/dependencies.py`
- `modules/users/api/dependencies.py`

Это нарушает принцип модульного монолита: код одного модуля не должен напрямую вызывать код другого модуля.

## Решение: Ports & Adapters (Hexagonal Architecture)

### Новые файлы

**`src/modules/users/ports.py`**
- Содержит `UserNotificationPort` — `typing.Protocol`
- Описывает контракт: что модуль `users` ожидает от сервиса уведомлений
- Методы: `send_login_code_email_task`, `send_welcome_email_task`
- Модуль `users` владеет интерфейсом (Dependency Inversion Principle)

**`src/core/dependencies.py`**
- Composition root для межмодульного связывания
- Единственное место в проекте, где разрешено импортировать из нескольких модулей одновременно
- `get_user_notification_service` — вызывает фабрику из `notifications` и возвращает результат как `UserNotificationPort`
- Не дублирует логику создания `UsersEmailService` — переиспользует `notifications/dependencies.py`

### Изменённые файлы

**`modules/users/manager.py`**
- Тип `email_service` изменён с `UsersEmailService` → `UserNotificationPort`
- Убран импорт `from modules.notifications.services.users_email import UsersEmailService`

**`modules/users/services/auth_service.py`**
- Тип `email_service` изменён с `UsersEmailService` → `UserNotificationPort`
- Убран импорт `from modules.notifications.services.users_email import UsersEmailService`

**`modules/users/dependencies.py`**
- `get_users_email_service` из `notifications` заменён на `get_user_notification_service` из `core`
- Убраны импорты из `modules.notifications`

**`modules/users/api/dependencies.py`**
- Аналогично `dependencies.py`

## Итоговая схема зависимостей

```
modules/users       →  core            (разрешено: core — общий слой)
modules/notifications →  core          (разрешено)
core                →  modules/*       (только в composition root)

modules/users       ✗  modules/notifications  (запрещено, устранено)
```

## Цепочка вызовов DI

```
FastAPI request
  → get_user_notification_service (core/dependencies.py)
      → get_users_email_service (notifications/dependencies.py)
          → UsersEmailService(EmailSettings(), background_tasks)
  → возвращается как UserNotificationPort в users-слой
```

## Ключевые принципы

- **Потребитель владеет интерфейсом**: `UserNotificationPort` живёт в `modules/users/ports.py`, а не в `notifications`
- **Structural subtyping**: `UsersEmailService` удовлетворяет протоколу без явного наследования (duck typing)
- **Единая точка связывания**: только `core/dependencies.py` знает про оба модуля
- **Без дублирования**: `core/dependencies.py` делегирует фабрике внутри `notifications`, не копирует логику
