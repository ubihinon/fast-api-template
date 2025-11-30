# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from db.session import get_session
# from repositories.user import UserRepository
# from services.user_service import UserService
#
# users_router = APIRouter(prefix='/users', tags=['users'])
#
#
# @users_router.post('/create')
# async def create_user(email: str, name: str, session: AsyncSession = Depends(get_session)):
#     service = UserService(UserRepository(session))
#     user = await service.register_user(email, name)
#     return {'user': user}
#
#
# @users_router.get(
#     '/{user_id}',
#     response_model=UserSchema,
#     responses={
#         200: {
#             'content': {'application/json': {}},
#         },
#         404: {'description': 'Not found'}
#     })
# async def get_user_by_id(user_id: int, session: AsyncSession = Depends(get_session)):
#     service = UserService(UserRepository(session))
#     user = await service.get_user_by_id(user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail='Not found')
#     return user
#
#
# @users_router.get('/1/{email}')
# async def get_user_by_email(email: str, session: AsyncSession = Depends(get_session)):
#     service = UserService(UserRepository(session))
#     user = await service.get_user(email)
#     return {'user': user}
#
#
# @users_router.get('/all')
# async def get_all_users(session: AsyncSession = Depends(get_session)):
#     service = UserService(UserRepository(session))
#     users = await service.get_users()
#     return {'data': users}
