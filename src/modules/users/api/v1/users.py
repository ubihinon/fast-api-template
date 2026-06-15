from fastapi import APIRouter

from modules.users.fastapi_users_config import fastapi_users
from modules.users.dtos.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

# /me and /{id}
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)


# users_router = APIRouter(prefix="/users", tags=["users"])
#
#
# @users_router.post("/create")
# async def create_user(email: str, name: str, session: AsyncSession = Depends(get_session)):
#     service = UserService(UserRepository(session))
#     user = await service.register_user(email, name)
#     return {"user": user}
#
#
# @users_router.get(
#     "/{user_id}",
#     response_model=UserSchema,
#     responses={
#         200: {
#             "content": {"application/json": {}},
#         },
#         404: {"description": "Not found"}
#     })
# async def get_user_by_id(user_id: int, session: AsyncSession = Depends(get_session)):
#     service = UserService(UserRepository(session))
#     user = await service.get_user_by_id(user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="Not found")
#     return user
#
#
# @users_router.get("/1/{email}")
# async def get_user_by_email(email: str, session: AsyncSession = Depends(get_session)):
#     service = UserService(UserRepository(session))
#     user = await service.get_user(email)
#     return {"user": user}
#
#
# @users_router.get("/all")
# async def get_all_users(session: AsyncSession = Depends(get_session)):
#     service = UserService(UserRepository(session))
#     users = await service.get_users()
#     return {"data": users}
