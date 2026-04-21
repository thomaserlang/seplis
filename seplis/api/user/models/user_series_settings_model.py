import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.models import Base


class MUserSeriesSettings(Base):
    __tablename__ = 'user_series_settings'

    user_id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=False
    )
    series_id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=False
    )
    subtitle_lang: Mapped[str | None] = mapped_column(sa.String)
    audio_lang: Mapped[str | None] = mapped_column(sa.String)
