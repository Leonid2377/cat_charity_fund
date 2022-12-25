from datetime import datetime
from typing import List, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def get_opened_charity_project(
    model: Union[CharityProject, Donation],
    session: AsyncSession
) -> List[Union[CharityProject, Donation]]:
    charity_project = await session.execute(
        select(
            model
        ).where(
            model.fully_invested == False  # noqa
        ).order_by(
            model.create_date
        )
    )
    return charity_project.scalars().all()


async def close_invested_object(
    obj_to_close: Union[CharityProject, Donation],
):
    obj_to_close.fully_invested = True
    obj_to_close.close_date = datetime.now()


async def invest_when_new_project(
    project: Union[CharityProject, Donation],
    session: AsyncSession
):
    db_model = (
        CharityProject if isinstance(project, Donation) else Donation
    )
    not_invested_objects = await get_opened_charity_project(db_model, session)  # noqa
    available_amount = project.full_amount

    if not_invested_objects:
        for not_invested_obj in not_invested_objects:
            need_to_invest = not_invested_obj.full_amount - not_invested_obj.invested_amount
            to_invest = (
                need_to_invest if need_to_invest < available_amount else available_amount
            )
            not_invested_obj.invested_amount += to_invest
            project.invested_amount += to_invest
            available_amount -= to_invest

            if not_invested_obj.full_amount == not_invested_obj.invested_amount:
                await close_invested_object(not_invested_obj)

            if not available_amount:
                await close_invested_object(project)
                break
        await session.commit()
        await session.refresh(project)
    return project
