from __future__ import annotations

from datetime import date as date_
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.model_base import Base


class MSeriesRatingHistory(Base):
    __tablename__ = 'series_rating_history'

    series_id: Mapped[int] = mapped_column(
        sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
    )
    date: Mapped[date_] = mapped_column(sa.Date, primary_key=True)
    rating: Mapped[Decimal] = mapped_column(sa.DECIMAL(4, 2))
    votes: Mapped[int] = mapped_column()
