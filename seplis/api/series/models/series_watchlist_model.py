from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.model_base import Base
from seplis.utils.sqlalchemy import UtcDateTime


class MSeriesWatchlist(Base):
    __tablename__ = 'series_watchlist'

    series_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey('series.id'), primary_key=True, autoincrement=False
    )
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey('users.id'), primary_key=True, autoincrement=False
    )
    created_at: Mapped[datetime] = mapped_column(UtcDateTime, nullable=False)
