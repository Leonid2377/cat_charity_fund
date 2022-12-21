from datetime import datetime
from sqlalchemy import Boolean, Column, CheckConstraint, DateTime, Integer

from app.core.db import Base


class BaseModel(Base):
    __abstract__ = True

    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, nullable=False, default=0)
    fully_invested = Column(Boolean, nullable=False, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

    __table_args__ = (
        CheckConstraint('invested_amount <= full_amount'),
    )
