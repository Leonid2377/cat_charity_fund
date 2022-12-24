from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def get_opened_donations(
        session: AsyncSession,
) -> List[Donation]:
    donations = await session.execute(
        select(
            Donation
        ).where(
            Donation.fully_invested == False  # noqa
        ).order_by(
            Donation.create_date
        )
    )
    return donations.scalars().all()


async def invest_when_new_project(
        project: CharityProject,
        session: AsyncSession,
) -> CharityProject:
    donations = await get_opened_donations(session)
    for donation in donations:
        donation_delta = (
            donation.full_amount - donation.invested_amount
        )
        project_balance = (
            project.full_amount - project.invested_amount
        )
        if project_balance <= donation_delta:
            donation.invested_amount += project_balance
            project.invested_amount += project_balance
            project.close_date = datetime.now()
            project.fully_invested = True
            session.add(donation)

            if project_balance == donation_delta:
                donation.close_date = datetime.now()
                donation.fully_invested = True
                session.add(donation)
            session.add(project)
            break
        else:
            project.invested_amount += donation_delta
            donation.invested_amount = donation.full_amount
            donation.close_date = datetime.now()
            donation.fully_invested = True
            session.add(donation)
    await session.commit()
    await session.refresh(project)
    return project


async def patch_project_with_full_investment(
        project: CharityProject,
        session: AsyncSession,
) -> CharityProject:
    if project.full_amount == project.invested_amount:
        project.fully_invested = True
        project.close_date = datetime.now()
        await session.commit()
        await session.refresh(project)
    return project
