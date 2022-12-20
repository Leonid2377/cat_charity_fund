from http import HTTPStatus
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject
from app.schemas.charity_project import CharityProjectUpdate


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    project_id = await (
        charity_project_crud.get_project_id_by_name(project_name, session))
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!'
        )


async def check_project_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    project = await charity_project_crud.get(project_id, session)
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден'
        )
    return project


async def check_project_before_edit(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession
) -> CharityProject:
    project = await check_project_exists(project_id, session)
    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )
    if obj_in.full_amount and obj_in.full_amount < project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Требуемая сумма не может быть меньше уже инвестированной'
        )
    return project


async def check_project_before_delete(
        project_id: int,
        session: AsyncSession
) -> CharityProject:
    project = await check_project_exists(project_id, session)
    if project.invested_amount != 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    return project
