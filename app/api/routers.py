from fastapi import APIRouter

from app.api.endpoints import project_router, donation_router, user_router


main_router = APIRouter()
main_router.include_router(
    project_router, prefix='/charity_project', tags=['Проекты']
)
main_router.include_router(
    donation_router, prefix='/donation', tags=['Пожертвования']
)
main_router.include_router(user_router)
