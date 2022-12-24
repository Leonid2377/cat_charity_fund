from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def get_opened_charity_project(
        session: AsyncSession,
) -> List[CharityProject]:
    charity_project = await session.execute(
        select(
            CharityProject
        ).where(
            CharityProject.fully_invested == False  # noqa
        ).order_by(
            CharityProject.create_date
        )
    )
    return charity_project.scalars().all()


async def invest_when_new_donation(
        donation: Donation,
        session: AsyncSession,
) -> Donation:
    charity_projects = await get_opened_charity_project(session)
    for project in charity_projects:
        project_delta = (
            project.full_amount - project.invested_amount
        )
        donation_balance = (
            donation.full_amount - donation.invested_amount
        )
        if donation_balance <= project_delta:
            project.invested_amount += donation_balance
            donation.invested_amount += donation_balance
            donation.close_date = datetime.now()
            donation.fully_invested = True

            if donation_balance == project_delta:
                project.close_date = datetime.now()
                project.fully_invested = True
                session.add(project)
            session.add(donation)
            break
        else:
            donation.invested_amount += project_delta
            project.invested_amount = project.full_amount
            project.close_date = datetime.now()
            project.fully_invested = True
            session.add(project)
    await session.commit()
    await session.refresh(donation)
    return donation
