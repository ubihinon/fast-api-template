async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
