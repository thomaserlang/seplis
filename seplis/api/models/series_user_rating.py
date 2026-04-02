from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from seplis.utils import datetime_now
from seplis.utils.sqlalchemy import UtcDateTime

from .base import Base


class MSeriesUserRating(Base):
    __tablename__ = 'user_series_ratings'

    user_id: Mapped[int] = mapped_column(autoincrement=False, primary_key=True)
    series_id: Mapped[int] = mapped_column(autoincrement=False, primary_key=True)
    rating: Mapped[int | None] = mapped_column()
    updated_at: Mapped[datetime | None] = mapped_column(
        UtcDateTime, default=datetime_now, onupdate=datetime_now
    )
