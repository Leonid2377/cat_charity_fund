from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_project_before_delete,
                                check_project_exists,
                                check_name_duplicate,
                                check_project_update)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charityproject import charity_project_crud
from app.models import CharityProject
from app.schemas.charityproject import (CharityProjectCreate,
                                        CharityProjectResponse,
                                        CharityProjectUpdate)
from app.services.investment import invest_when_new_project

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):

    await check_name_duplicate(charity_project.name, session)

    new_charity_project = await charity_project_crud.create(
        charity_project, session)

    await invest_when_new_project(new_charity_project, session)
    return new_charity_project


@router.get(
    '/',
    response_model=list[CharityProjectResponse],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    return await charity_project_crud.get_multi(session)


@router.patch(
    '/{charity_project_id}',
    response_model=CharityProjectResponse,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
        charity_project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):

    charity_project = await check_project_exists(
        charity_project_id, session
    )

    await check_project_update(
        charity_project, obj_in, session
    )
    charity_project: CharityProject = (
        await charity_project_crud.update(
            charity_project, obj_in, session
        )
    )

    return charity_project


@router.delete(
    '/{charity_project_id}',
    response_model=CharityProjectResponse,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
        charity_project_id: int,
        session: AsyncSession = Depends(get_async_session),
):

    await check_project_exists(charity_project_id,
                               session)
    charity_project = await check_project_before_delete(
        charity_project_id, session)
    charity_project = await charity_project_crud.remove(
        charity_project, session)
    return charity_project
