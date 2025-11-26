from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/hello/{name}')
async def say_hello(name: str):
    return {'message': f'Hello {name}'}


@app.post('/user/create')
async def create_user(email: str, name: str):
    return await UserDAL(session=AsyncSession(engine)).create(email, name)

@app.post('/user/{user_id}')
async def get_user_by_id(user_id: int):
    return await UserDAL(session=AsyncSession(engine)).get_by_id(user_id)

@app.post('/user/1/{email}')
async def get_user_by_email(email: str):
    return await UserDAL(session=AsyncSession(engine)).get_by_email(email)


@app.post('/user/all')
async def get_all_users():
    return await UserDAL(session=AsyncSession(engine)).all()
