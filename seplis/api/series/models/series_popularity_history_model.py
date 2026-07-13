from __future__ import annotations

from datetime import date as date_
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.model_base import Base


class MSeriesPopularityHistory(Base):
    __tablename__ = 'series_popularity_history'

    series_id: Mapped[int] = mapped_column(
        sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
    )
    date: Mapped[date_] = mapped_column(sa.Date, primary_key=True)
    popularity: Mapped[Decimal] = mapped_column(sa.DECIMAL(precision=12, scale=4))
