from datetime import date
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MSeriesRatingHistory(Base):
    __tablename__ = 'series_rating_history'

    series_id: Mapped[int] = mapped_column(
        sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
    )
    date: Mapped[date] = mapped_column(sa.Date, primary_key=True)
    rating: Mapped[Decimal] = mapped_column(sa.DECIMAL(4, 2))
    votes: Mapped[int] = mapped_column()
