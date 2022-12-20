from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_name_duplicate, check_project_before_edit,
    check_project_before_delete
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.services.investing import investing
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectUpdate,
    CharityProjectDB
)

router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True
)
async def get_all_projects(
        session: AsyncSession = Depends(get_async_session)
):
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_project(
        project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session)
):
    await check_name_duplicate(project.name, session)
    new_project = await charity_project_crud.create(project, session)
    await investing(session)
    await session.refresh(new_project)
    return new_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def partially_update_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session)
):
    project = await check_project_before_edit(project_id, obj_in, session)
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    project = await charity_project_crud.update(project, obj_in, session)
    await investing(session)
    await session.refresh(project)
    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def remove_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    project = await check_project_before_delete(project_id, session)
    return await charity_project_crud.remove(project, session)
